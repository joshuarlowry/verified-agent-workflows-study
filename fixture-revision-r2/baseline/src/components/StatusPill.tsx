import { STATUS_LABELS, type WorkItemStatus } from "../../shared/domain.js";

export default function StatusPill({ status }: { status: WorkItemStatus }) {
  return <span className={`pill pill-${status}`}>{STATUS_LABELS[status]}</span>;
}
