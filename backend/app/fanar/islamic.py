"""Islamic-RAG ruling: sourced answer with inline citation tags parsed out.

Fanar's Islamic-RAG returns the ruling with citations as inline tags, e.g.
`<quran_start>…verse…<quran_end>` (and hadith tags). We split those into a structured
citations list and a clean prose version. We NEVER trust its arithmetic (HARD RULE 3).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from app.fanar.chat import chat
from app.fanar.models import ISLAMIC

_CITATION = re.compile(r"<(quran|hadith)_start>(.*?)<\1_end>", re.DOTALL)


@dataclass
class Citation:
    source: str   # "quran" | "hadith"
    text: str

    def to_dict(self) -> dict:
        return {"source": self.source, "text": self.text}


def parse_citations(raw: str) -> Tuple[str, List[Citation]]:
    """Pure: split inline <source_start>..<source_end> tags into a clean string + citations."""
    citations = [Citation(m.group(1), m.group(2).strip()) for m in _CITATION.finditer(raw)]
    # Keep the quoted text inline (in guillemets) but strip the wrapper tags.
    clean = _CITATION.sub(lambda m: f"«{m.group(2).strip()}»", raw).strip()
    return clean, citations


# Ask the Islamic model to END with an explicit per-heir fraction list, so the verifier
# can reliably reconcile its stated shares against the deterministic calculator.
_RULING_SUFFIX = (
    "\n\nأجب بالحكم الشرعي مع الأدلة، ثم في سطر أخير اذكر بوضوح نصيب كل وارث ككسر من "
    "التركة بهذه الصيغة فقط: [الزوجة: 1/8، الابن: ...]."
)


def get_ruling(question: str, model: str = ISLAMIC) -> Tuple[str, List[Citation], str]:
    """Return (clean_ruling, citations, raw_text)."""
    raw = chat([{"role": "user", "content": question + _RULING_SUFFIX}],
               model=model, max_tokens=700)
    clean, citations = parse_citations(raw)
    return clean, citations, raw
