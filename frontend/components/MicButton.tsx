"use client";
import { useRef, useState } from "react";
import { MicIcon, StopIcon, SpinnerIcon } from "./icons";

type State = "idle" | "recording" | "denied";

export function MicButton({
  busy,
  onRecorded,
}: {
  busy: boolean;
  onRecorded: (blob: Blob) => void;
}) {
  const [state, setState] = useState<State>("idle");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      chunksRef.current = [];
      rec.ondataavailable = (e) => e.data.size && chunksRef.current.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        onRecorded(new Blob(chunksRef.current, { type: "audio/webm" }));
      };
      rec.start();
      recorderRef.current = rec;
      setState("recording");
    } catch {
      setState("denied");
    }
  }

  function stop() {
    recorderRef.current?.stop();
    setState("idle");
  }

  const recording = state === "recording";
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        disabled={busy}
        onClick={recording ? stop : start}
        aria-label={recording ? "إيقاف التسجيل" : "ابدأ تسجيل القراءة"}
        className={`grid h-20 w-20 cursor-pointer place-items-center rounded-full text-white shadow-soft transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-60 ${
          recording ? "bg-rose-500 animate-pulse-glow" : "bg-accent hover:bg-accent-light"
        }`}
      >
        {busy ? (
          <SpinnerIcon className="h-8 w-8" />
        ) : recording ? (
          <StopIcon className="h-8 w-8" />
        ) : (
          <MicIcon className="h-8 w-8" />
        )}
      </button>
      <span className="text-sm font-medium text-slate-600">
        {busy ? "جارٍ التحليل…" : recording ? "يستمع… اضغط للإيقاف" : "اضغط لقراءة النص"}
      </span>
      {state === "denied" && (
        <span className="text-xs text-rose-500">تعذّر الوصول للميكروفون — جرّب «عرض توضيحي»</span>
      )}
    </div>
  );
}
