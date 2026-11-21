import { useEffect, useState } from "react";
import type { Mode } from "../graph";

const INTERVAL = 1600; // milliseconds a step stays when playing

/** Step through a trial: play, the step slider, and the switch between steps and final state. */
export function Scrubber(props: {
  steps: number;
  step: number;
  mode: Mode;
  onStep: (step: number) => void;
  onMode: (mode: Mode) => void;
}) {
  const { steps, step, mode, onStep, onMode } = props;
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const t = setTimeout(() => (step + 1 < steps ? onStep(step + 1) : setPlaying(false)), INTERVAL);
    return () => clearTimeout(t);
  }, [playing, step, steps, onStep]);
  return (
    <div className="scrubber">
      <button
        type="button"
        className="scrubber-play"
        disabled={mode === "topology"}
        onClick={() => {
          if (!playing && step + 1 >= steps) onStep(0);
          setPlaying(!playing);
        }}
      >
        {playing ? "pause" : "play"}
      </button>
      <input
        className="scrubber-range"
        type="range"
        min={0}
        max={steps - 1}
        value={step}
        disabled={mode === "topology"}
        onChange={(e) => onStep(Number(e.target.value))}
        aria-label="step"
      />
      <button
        type="button"
        className="scrubber-mode"
        onClick={() => onMode(mode === "dynamics" ? "topology" : "dynamics")}
      >
        {mode === "dynamics" ? "final state" : "steps"}
      </button>
    </div>
  );
}
