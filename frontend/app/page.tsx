"use client";
import { AnimatePresence, motion } from "framer-motion";

import { useApp, type Screen } from "@/components/AppProvider";
import { PathScreen } from "@/components/screens/PathScreen";
import { SessionScreen } from "@/components/screens/SessionScreen";
import { ResultsScreen } from "@/components/screens/ResultsScreen";
import { PracticeScreen } from "@/components/screens/PracticeScreen";
import { ProgressScreen } from "@/components/screens/ProgressScreen";
import { TraceScreen } from "@/components/screens/TraceScreen";

const SCREENS: Record<Screen, () => JSX.Element | null> = {
  path: PathScreen,
  session: SessionScreen,
  results: ResultsScreen,
  practice: PracticeScreen,
  progress: ProgressScreen,
  trace: TraceScreen,
};

export default function Page() {
  const { screen } = useApp();
  const Screen = SCREENS[screen];

  return (
    <AnimatePresence mode="wait">
      <motion.main
        key={screen}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.22, ease: "easeOut" }}
      >
        <Screen />
      </motion.main>
    </AnimatePresence>
  );
}
