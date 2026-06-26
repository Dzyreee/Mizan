"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import * as api from "@/lib/api";
import { LESSONS, lessonById, type Lesson } from "@/lib/lessons";
import { libraryCandidates, librarySrc } from "@/lib/library";
import { sampleProgress } from "@/lib/sample";
import type { AdaptResult, AssessResult, Progress } from "@/lib/types";

export type Screen =
  | "path"
  | "session"
  | "results"
  | "practice"
  | "progress"
  | "trace";

export type NodeState = "completed" | "current" | "locked";

// Mocked gamification — there is no backend lesson-map/streak/stars concept.
interface Game {
  completed: number[];
  streak: number;
  lastPracticeDate: string | null; // YYYY-MM-DD
  stars: number;
}

const GAME_KEY = "naghami-game";
const DEFAULT_GAME: Game = { completed: [], streak: 0, lastPracticeDate: null, stars: 0 };

const todayStr = () => new Date().toISOString().slice(0, 10);
const yesterdayStr = () => {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
};
const starsFor = (accuracyPct: number) => (accuracyPct >= 90 ? 3 : accuracyPct >= 70 ? 2 : 1);

interface AppCtx {
  online: boolean | null;
  screen: Screen;
  go: (s: Screen) => void;

  lessons: Lesson[];
  activeLesson: Lesson | undefined;
  nodeState: (id: number) => NodeState;

  assess: AssessResult | null;
  adapt: AdaptResult | null;
  busyAssess: boolean;
  busyAdapt: boolean;
  note: string | null;

  // Fanar-picked illustrations (from the static library — no live image gen).
  sessionImage: string | null;
  poemImage: string | null;

  game: Game;
  progress: Progress | null;

  openNode: (id: number) => void;
  runAudio: (blob: Blob) => void;
  runDemo: () => void;
  toResults: () => void;
  toPractice: () => void;
  finishLesson: () => void;
}

const Ctx = createContext<AppCtx | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [online, setOnline] = useState<boolean | null>(null);
  const [screen, setScreen] = useState<Screen>("path");
  const [activeId, setActiveId] = useState<number | null>(null);
  const [assess, setAssess] = useState<AssessResult | null>(null);
  const [adapt, setAdapt] = useState<AdaptResult | null>(null);
  const [busyAssess, setBusyAssess] = useState(false);
  const [busyAdapt, setBusyAdapt] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [sessionImage, setSessionImage] = useState<string | null>(null);
  const [poemImage, setPoemImage] = useState<string | null>(null);
  const [game, setGame] = useState<Game>(DEFAULT_GAME);
  const [progress, setProgress] = useState<Progress | null>(sampleProgress);

  // Cache the picked image per lesson so re-opening a node is instant.
  const imgCache = useRef<Map<number, string>>(new Map());

  // Restore mocked game state.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(GAME_KEY);
      if (raw) setGame({ ...DEFAULT_GAME, ...JSON.parse(raw) });
    } catch {
      /* ignore */
    }
  }, []);

  // Health check + live progress.
  useEffect(() => {
    api.health().then((ok) => {
      setOnline(ok);
      if (ok) api.getProgress().then(setProgress).catch(() => {});
    });
  }, []);

  const persistGame = useCallback((g: Game) => {
    setGame(g);
    try {
      localStorage.setItem(GAME_KEY, JSON.stringify(g));
    } catch {
      /* ignore */
    }
  }, []);

  const activeLesson = lessonById(activeId);

  const nodeState = useCallback(
    (id: number): NodeState => {
      if (game.completed.includes(id)) return "completed";
      const firstIncomplete = LESSONS.find((l) => !game.completed.includes(l.id));
      if (firstIncomplete && firstIncomplete.id === id) return "current";
      return "locked";
    },
    [game.completed],
  );

  const go = useCallback((s: Screen) => setScreen(s), []);

  // Ask Fanar to pick the best library image for some text (fast). null on any failure.
  const pickImage = useCallback(async (text: string): Promise<string | null> => {
    try {
      const { id } = await api.pickIllustration(text, libraryCandidates());
      return librarySrc(id);
    } catch {
      return null;
    }
  }, []);

  const openNode = useCallback(
    (id: number) => {
      setActiveId(id);
      setAssess(null);
      setAdapt(null);
      setNote(null);
      setPoemImage(null);
      setScreen("session");

      const lesson = lessonById(id);
      if (!lesson) return;
      const cached = imgCache.current.get(id);
      if (cached) {
        setSessionImage(cached);
        return;
      }
      setSessionImage(null);
      void pickImage(lesson.passage).then((src) => {
        if (src) imgCache.current.set(id, src);
        setSessionImage(src);
      });
    },
    [pickImage],
  );

  // Shared assess runner — never falls back to mismatched sample data on error.
  const runAssess = useCallback(
    async (call: () => Promise<AssessResult>) => {
      setNote(null);
      setBusyAssess(true);
      setAdapt(null);
      try {
        setAssess(await call());
      } catch (e) {
        setNote((e as Error).message);
      } finally {
        setBusyAssess(false);
      }
    },
    [],
  );

  const runAudio = useCallback(
    (blob: Blob) => {
      if (!activeLesson) return;
      void runAssess(() => api.assessAudio(activeLesson.passage, blob));
    },
    [activeLesson, runAssess],
  );

  const runDemo = useCallback(() => {
    if (!activeLesson) return;
    void runAssess(() => api.assessTranscript(activeLesson.passage, activeLesson.demoMisread));
  }, [activeLesson, runAssess]);

  const toResults = useCallback(() => setScreen("results"), []);

  // Results "Continue" → generate the adaptive exercise (poem + TTS), then show Practice.
  // Skip live Oryx-IG image gen (slow); Fanar picks a library image for the poem instead.
  const toPractice = useCallback(async () => {
    setScreen("practice");
    if (!assess?.diagnosis) return;
    setNote(null);
    setBusyAdapt(true);
    setPoemImage(null);
    try {
      const ad = await api.adapt(assess.diagnosis, { includeImage: false, includeAudio: false });
      setAdapt(ad);
      const poem = ad.generated.verse || ad.plan.practice_passage || "";
      if (poem) void pickImage(poem).then(setPoemImage);
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusyAdapt(false);
    }
  }, [assess, pickImage]);

  // Practice "Finish" → mark node complete, bump streak/stars (mocked), back to path.
  const finishLesson = useCallback(() => {
    if (activeId != null) {
      const accuracy = assess?.error_map.accuracy_pct ?? 0;
      const completed = game.completed.includes(activeId)
        ? game.completed
        : [...game.completed, activeId];
      const today = todayStr();
      let streak = game.streak;
      if (game.lastPracticeDate !== today) {
        streak = game.lastPracticeDate === yesterdayStr() ? game.streak + 1 : 1;
      }
      persistGame({
        completed,
        streak,
        lastPracticeDate: today,
        stars: game.stars + starsFor(accuracy),
      });
    }
    setScreen("path");
  }, [activeId, assess, game, persistGame]);

  const value = useMemo<AppCtx>(
    () => ({
      online,
      screen,
      go,
      lessons: LESSONS,
      activeLesson,
      nodeState,
      assess,
      adapt,
      busyAssess,
      busyAdapt,
      note,
      sessionImage,
      poemImage,
      game,
      progress,
      openNode,
      runAudio,
      runDemo,
      toResults,
      toPractice,
      finishLesson,
    }),
    [
      online, screen, go, activeLesson, nodeState, assess, adapt, busyAssess,
      busyAdapt, note, sessionImage, poemImage, game, progress, openNode, runAudio,
      runDemo, toResults, toPractice, finishLesson,
    ],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useApp(): AppCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("useApp must be used within AppProvider");
  return v;
}
