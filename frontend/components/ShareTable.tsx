import type { ShareRow, Basis } from "@/lib/types";

const HEIR_AR: Record<string, [string, string]> = {
  // [singular, plural]
  husband: ["الزوج", "الزوج"],
  wife: ["الزوجة", "الزوجات"],
  son: ["ابن", "الأبناء"],
  daughter: ["بنت", "البنات"],
  father: ["الأب", "الأب"],
  mother: ["الأم", "الأم"],
};

const BASIS_AR: Record<Basis, string> = {
  fard: "فرض",
  residue: "تعصيب",
  awl: "عول",
  radd: "ردّ",
};

function heirLabel(heir: string, count: number) {
  const pair = HEIR_AR[heir];
  if (!pair) return heir;
  return count > 1 ? `${count} ${pair[1]}` : pair[0];
}

function money(n: number, currency: string) {
  return `${n.toLocaleString("en-US", { maximumFractionDigits: 2 })} ${currency}`;
}

export function ShareTable({ shares }: { shares: ShareRow[] }) {
  return (
    <table className="w-full border-collapse" dir="rtl">
      <thead>
        <tr className="text-ink-soft">
          <th className="label text-right font-normal pb-2">الوارث</th>
          <th className="label text-center font-normal pb-2">الأساس</th>
          <th className="label text-left font-normal pb-2">النصيب</th>
          <th className="label text-left font-normal pb-2">المبلغ</th>
        </tr>
      </thead>
      <tbody>
        {shares.map((s) => (
          <tr key={s.heir} className="border-t border-line">
            <td className="py-2.5 font-arabic text-lg text-ink">{heirLabel(s.heir, s.count)}</td>
            <td className="py-2.5 text-center">
              <span className="font-arabic text-sm text-brass">{BASIS_AR[s.basis]}</span>
            </td>
            <td className="py-2.5 text-left font-mono text-ink tnum" title={`= ${s.fraction}`}>
              {s.ratio}
            </td>
            <td className="py-2.5 text-left font-mono text-ink tnum">{money(s.amount_total, s.currency)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
