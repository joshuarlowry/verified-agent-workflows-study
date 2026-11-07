import { useState } from "react";
import {
  STATUS_LABELS,
  WORK_ITEM_STATUSES,
  type WorkItemStatus,
} from "../../shared/domain.js";
import { ApiError, readErrorMessage } from "../api-client.js";

export interface ItemFormValues {
  title: string;
  notes: string;
  status: WorkItemStatus;
  /** Empty string means "no due date"; converted to null for the API. */
  dueDate: string;
}

interface ItemFormProps {
  /** Prefill (edit mode) - omit for creation defaults. */
  initial?: Partial<ItemFormValues>;
  submitLabel: string;
  busyLabel?: string;
  onSubmit: (values: ItemFormValues) => Promise<void>;
  onCancel?: () => void;
}

const DEFAULTS: ItemFormValues = {
  title: "",
  notes: "",
  status: "open",
  dueDate: "",
};

/**
 * Baseline failure behavior (documented): on a failed save the form stays
 * open, the entered values are preserved, and the API error is surfaced as
 * a `role="alert"` banner plus per-field messages when provided.
 */
export default function ItemForm({
  initial,
  submitLabel,
  busyLabel = "Saving…",
  onSubmit,
  onCancel,
}: ItemFormProps) {
  const [values, setValues] = useState<ItemFormValues>({ ...DEFAULTS, ...initial });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function set<K extends keyof ItemFormValues>(key: K, value: ItemFormValues[K]) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setFieldErrors({});
    try {
      await onSubmit(values);
    } catch (err: unknown) {
      setError(readErrorMessage(err, "Saving failed. Your input is preserved - try again."));
      if (err instanceof ApiError && err.fields) {
        setFieldErrors(err.fields);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={(e) => void handleSubmit(e)} noValidate className="item-form">
      {error ? (
        <p className="banner banner-error" role="alert">
          {error}
        </p>
      ) : null}
      <div className="field">
        <label htmlFor="item-title">Title</label>
        <input
          id="item-title"
          name="title"
          type="text"
          value={values.title}
          aria-invalid={fieldErrors.title ? true : undefined}
          aria-describedby={fieldErrors.title ? "item-title-error" : undefined}
          onChange={(e) => set("title", e.target.value)}
        />
        {fieldErrors.title ? (
          <p className="field-error" id="item-title-error">
            {fieldErrors.title}
          </p>
        ) : null}
      </div>
      <div className="field">
        <label htmlFor="item-status">Status</label>
        <select
          id="item-status"
          name="status"
          value={values.status}
          onChange={(e) => set("status", e.target.value as WorkItemStatus)}
        >
          {WORK_ITEM_STATUSES.map((status) => (
            <option key={status} value={status}>
              {STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="item-due-date">Due date</label>
        <input
          id="item-due-date"
          name="dueDate"
          type="date"
          value={values.dueDate}
          aria-invalid={fieldErrors.dueDate ? true : undefined}
          aria-describedby={fieldErrors.dueDate ? "item-due-date-error" : undefined}
          onChange={(e) => set("dueDate", e.target.value)}
        />
        {fieldErrors.dueDate ? (
          <p className="field-error" id="item-due-date-error">
            {fieldErrors.dueDate}
          </p>
        ) : null}
      </div>
      <div className="field">
        <label htmlFor="item-notes">Notes</label>
        <textarea
          id="item-notes"
          name="notes"
          value={values.notes}
          aria-invalid={fieldErrors.notes ? true : undefined}
          aria-describedby={fieldErrors.notes ? "item-notes-error" : undefined}
          onChange={(e) => set("notes", e.target.value)}
        />
        {fieldErrors.notes ? (
          <p className="field-error" id="item-notes-error">
            {fieldErrors.notes}
          </p>
        ) : null}
      </div>
      <div className="item-actions">
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? busyLabel : submitLabel}
        </button>
        {onCancel ? (
          <button type="button" className="btn" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
