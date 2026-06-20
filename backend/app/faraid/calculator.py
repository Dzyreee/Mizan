"""Deterministic Islamic inheritance (faraid) calculator.

SCOPE (prototype core set):
    Heirs handled: husband / wife(s), sons, daughters, father, mother.
    Rules handled: Quranic fixed shares (furud), agnatic residue (ta'sib, 2:1 male:female),
                   'awl (shares exceed the estate -> proportional reduction),
                   radd (surplus with no agnate -> returned to non-spouse sharers),
                   the two Umariyyatan/Gharrawayn cases (spouse + mother + father).

OUT OF SCOPE (deferred to Fanar-Sadiq as the authority, documented for the demo):
    grandfather/grandmother, grandchildren, full/paternal/maternal siblings and their
    interactions (e.g. grandfather-vs-siblings, mushtaraka), hermaphrodite/khuntha,
    missing person (mafqud), pregnancy (haml), non-Muslim/impediments, bequests > 1/3.

All arithmetic is exact via fractions.Fraction.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Dict, List, Optional

ZERO = Fraction(0)
ONE = Fraction(1)


@dataclass(frozen=True)
class Heirs:
    """Who survives the deceased. wives is a count (0-4); husband is exclusive with wives."""

    husband: bool = False
    wives: int = 0
    sons: int = 0
    daughters: int = 0
    father: bool = False
    mother: bool = False

    def validate(self) -> None:
        if self.husband and self.wives:
            raise ValueError("The deceased cannot have both a husband and wives.")
        if min(self.wives, self.sons, self.daughters) < 0:
            raise ValueError("Heir counts cannot be negative.")
        if self.wives > 4:
            raise ValueError("A man may have at most 4 wives.")
        if not (self.husband or self.wives or self.sons or self.daughters
                or self.father or self.mother):
            raise ValueError("No heirs provided.")


@dataclass
class Share:
    """A heir class's allocation. `fraction` is the class total; `each` is per individual.

    `basis` says HOW the share arose, which the verifier uses to decide what is independently
    checkable against the Islamic ruling:
      "fard"    — a fixed Quranic share (Sadiq states it reliably; hard-checked)
      "residue" — agnatic residue / ta'sib arithmetic (deterministic engine owns it)
      "awl"     — proportionally reduced ('awl)
      "radd"    — proportionally increased (radd)
    """

    heir: str
    count: int
    fraction: Fraction
    each: Fraction
    basis: str = "fard"

    def as_ratio(self, base: int) -> str:
        return f"{int(self.fraction * base)}/{base}"


@dataclass
class Distribution:
    shares: List[Share]
    kind: str  # "normal" | "awl" | "radd"
    base: int  # common denominator (asl al-mas'ala) for display
    note: Optional[str] = None

    def total(self) -> Fraction:
        return sum((s.fraction for s in self.shares), ZERO)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "base": self.base,
            "note": self.note,
            "total": str(self.total()),
            "shares": [
                {
                    "heir": s.heir,
                    "count": s.count,
                    "fraction": str(s.fraction),
                    "each": str(s.each),
                    "ratio": s.as_ratio(self.base),
                    "basis": s.basis,
                }
                for s in self.shares
            ],
        }

    def render(self) -> str:
        lines = [f"Distribution ({self.kind}), base /{self.base}:"]
        for s in self.shares:
            who = s.heir if s.count == 1 else f"{s.count}x {s.heir}"
            lines.append(f"  {who:<16} {str(s.fraction):>6}  (each {s.each})")
        lines.append(f"  {'TOTAL':<16} {str(self.total()):>6}")
        if self.note:
            lines.append(f"  note: {self.note}")
        return "\n".join(lines)


_ORDER = {"husband": 0, "wife": 1, "son": 2, "daughter": 3, "father": 4, "mother": 5}


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def compute_inheritance(heirs: Heirs) -> Distribution:
    heirs.validate()
    has_desc = heirs.sons > 0 or heirs.daughters > 0
    has_male_desc = heirs.sons > 0

    fixed: Dict[str, Fraction] = {}
    basis: Dict[str, str] = {}   # heir -> "fard" | "residue" | "awl" | "radd"
    note: Optional[str] = None

    # --- spouse (always a fixed Quranic share) ---
    spouse_share = ZERO
    if heirs.husband:
        spouse_share = Fraction(1, 4) if has_desc else Fraction(1, 2)
        fixed["husband"] = spouse_share
        basis["husband"] = "fard"
    elif heirs.wives > 0:
        spouse_share = Fraction(1, 8) if has_desc else Fraction(1, 4)
        fixed["wife"] = spouse_share
        basis["wife"] = "fard"

    # --- mother (fixed) ---
    is_umar = heirs.mother and heirs.father and spouse_share > 0 and not has_desc
    if heirs.mother:
        if is_umar:
            # Umariyyatan: 1/3 of the residue AFTER the spouse, not 1/3 of the whole.
            fixed["mother"] = (ONE - spouse_share) / 3
            note = "Umariyyatan: mother takes 1/3 of the residue after the spouse's share."
        elif has_desc:
            fixed["mother"] = Fraction(1, 6)
        else:
            fixed["mother"] = Fraction(1, 3)
        basis["mother"] = "fard"

    # --- daughters as Quranic sharers (fixed; only when there is no son) ---
    if heirs.daughters > 0 and heirs.sons == 0:
        fixed["daughter"] = Fraction(1, 2) if heirs.daughters == 1 else Fraction(2, 3)
        basis["daughter"] = "fard"

    # --- father takes a fixed 1/6 whenever a descendant exists ---
    if heirs.father and has_desc:
        fixed["father"] = Fraction(1, 6)
        basis["father"] = "fard"

    total_fixed = sum(fixed.values(), ZERO)

    # --- 'AWL: fixed shares exceed the estate -> reduce all proportionally ---
    if total_fixed > ONE:
        scaled = {k: v / total_fixed for k, v in fixed.items()}
        awl_basis = {k: "awl" for k in scaled}
        return _finalize(
            heirs, scaled, awl_basis, "awl",
            "'Awl: fixed shares exceed unity; every share is reduced proportionally.",
        )

    residue = ONE - total_fixed
    shares = dict(fixed)
    kind = "normal"

    # --- assign residue to the nearest agnate (asaba) ---
    if heirs.sons > 0:
        shares["children_residue"] = residue  # split 2:1 in _finalize (basis "residue")
        residue = ZERO
    elif heirs.father:
        # father is the agnate: his fixed 1/6 (if any) plus the residue -> residuary
        shares["father"] = shares.get("father", ZERO) + residue
        basis["father"] = "residue"
        residue = ZERO

    # --- RADD: leftover with no agnate -> return to non-spouse sharers ---
    if residue > 0:
        non_spouse = {k: v for k, v in shares.items() if k not in ("husband", "wife")}
        denom = sum(non_spouse.values(), ZERO)
        if denom == 0:
            note = "Only a spouse inherits; the residue passes to the public treasury (bayt al-mal)."
        else:
            remaining = ONE - spouse_share
            for k in non_spouse:
                shares[k] = non_spouse[k] / denom * remaining
                basis[k] = "radd"
            kind = "radd"
            note = "Radd: the surplus is returned proportionally to the non-spouse sharers."

    return _finalize(heirs, shares, basis, kind, note)


def _finalize(heirs: Heirs, class_shares: Dict[str, Fraction], basis: Dict[str, str],
              kind: str, note: Optional[str]) -> Distribution:
    class_shares = dict(class_shares)
    out: List[Share] = []

    # children take the residue together, 2:1 male:female (residuary basis)
    if "children_residue" in class_shares:
        total = class_shares.pop("children_residue")
        units = heirs.sons * 2 + heirs.daughters
        unit = total / units
        if heirs.sons:
            out.append(Share("son", heirs.sons, unit * 2 * heirs.sons, unit * 2, "residue"))
        if heirs.daughters:
            out.append(Share("daughter", heirs.daughters, unit * heirs.daughters, unit, "residue"))

    counts = {
        "husband": 1, "wife": heirs.wives, "son": heirs.sons,
        "daughter": heirs.daughters, "father": 1, "mother": 1,
    }
    for key, frac in class_shares.items():
        c = counts[key]
        out.append(Share(key, c, frac, frac / c, basis.get(key, "fard")))

    out.sort(key=lambda s: _ORDER[s.heir])

    base = 1
    for s in out:
        base = _lcm(base, s.fraction.denominator)
    return Distribution(out, kind, base, note)
