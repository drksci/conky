import type { Region as RegionData } from "../graph";
import { useSeen } from "../frame-context";

export interface RegionNodeData extends Record<string, unknown> {
  region: RegionData;
}

/** A labelled region inside a space or beside it: the notes shown to a space, those not shown,
 * the desk before any question, or the term pages. Its label counts the members there now. */
export function Region({ data }: { data: RegionNodeData }) {
  const seen = useSeen();
  const { region } = data;
  const here = region.members.filter((m) => seen.frame.shown.has(m)).length;
  return (
    <div className={`region region-${region.kind} ${here ? "" : "is-hidden"}`} data-region={region.id}>
      <span className="region-label">
        {region.label} <span className="region-count">{here}</span>
      </span>
    </div>
  );
}
