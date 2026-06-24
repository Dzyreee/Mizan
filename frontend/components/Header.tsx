import { BookIcon, ShieldIcon } from "./icons";

export function Header({ online }: { online: boolean | null }) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-brand text-white shadow-soft">
          <BookIcon className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold leading-none text-ink">
            نَغَمي <span className="text-base font-semibold text-brand mono">Naghami</span>
          </h1>
          <p className="mt-1 text-sm text-slate-600">رفيق القراءة الذكي للأطفال</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="chip border border-emerald-200 bg-emerald-50 text-emerald-700">
          <ShieldIcon className="h-4 w-4" />
          أداة دعم للقراءة — ليست أداة تشخيص
        </span>
        <span
          className="chip border border-slate-200 bg-white text-slate-600"
          title={online === null ? "جارٍ الفحص" : online ? "الخادم متصل" : "وضع العرض (بيانات تجريبية)"}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              online === null ? "bg-slate-300" : online ? "bg-emerald-500" : "bg-amber-400"
            }`}
          />
          {online === null ? "…" : online ? "متصل" : "وضع العرض"}
        </span>
      </div>
    </header>
  );
}
