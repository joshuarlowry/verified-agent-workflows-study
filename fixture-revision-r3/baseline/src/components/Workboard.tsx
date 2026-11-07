import { useEffect, useRef, useState } from "react";
import { api, readErrorMessage } from "../api-client.js";
import { useJson } from "../hooks/useJson.js";
import type {
  ItemListResponse,
  MeResponse,
  WorkItem,
  WorkspaceSummary,
} from "../../shared/types.js";
import ItemForm, { type ItemFormValues } from "./ItemForm.js";
import StatusPill from "./StatusPill.js";

const ROLE_LABELS: Record<string, string> = {
  owner: "Owner",
  member: "Member",
};

export default function Workboard() {
  const me = useJson<MeResponse>("/api/me");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // Advance synchronously at the selection event, not in an effect: an ABA
  // return to the same id is a different selection lifetime.
  const selectedIdRef = useRef<string | null>(null);
  const selectionGeneration = useRef(0);
  const formGeneration = useRef(0);
  const deleteGeneration = useRef(0);
  const [live, setLive] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [confirmingId, setConfirmingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const workspaces: WorkspaceSummary[] = me.data?.workspaces ?? [];

  useEffect(() => {
    if (!me.data) return;
    const ids = me.data.workspaces.map((w) => w.id);
    const current = selectedIdRef.current;
    const next = current !== null && ids.includes(current) ? current : (ids[0] ?? null);
    if (next !== current) changeSelection(next);
  }, [me.data]);

  const selected = workspaces.find((w) => w.id === selectedId) ?? null;
  const items = useJson<ItemListResponse>(selectedId ? `/api/workspaces/${selectedId}/items` : null);

  function changeSelection(next: string | null) {
    if (selectedIdRef.current !== next) {
      selectedIdRef.current = next;
      selectionGeneration.current += 1;
      formGeneration.current += 1;
      deleteGeneration.current += 1;
    }
    setSelectedId(next);
  }

  function startFormAction(): () => boolean {
    const selection = selectionGeneration.current;
    const form = formGeneration.current;
    return () => selectionGeneration.current === selection && formGeneration.current === form;
  }

  function announce(message: string) {
    setLive(message);
  }

  async function createWorkspace(name: string): Promise<void> {
    await api<WorkspaceSummary>("/api/workspaces", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    await me.reload();
    announce("Workspace created.");
  }

  function valuesToPayload(values: ItemFormValues): string {
    return JSON.stringify({
      title: values.title,
      notes: values.notes,
      status: values.status,
      dueDate: values.dueDate === "" ? null : values.dueDate,
    });
  }

  // Completion belongs to the originating selection and form lifetime.
  // The request itself remains addressed to its original workspace.
  async function createItem(values: ItemFormValues, isCurrent: () => boolean): Promise<void> {
    const scope = selectedIdRef.current;
    if (!scope) return;
    await api<WorkItem>(`/api/workspaces/${scope}/items`, {
      method: "POST",
      body: valuesToPayload(values),
    });
    if (!isCurrent()) return;
    items.reload();
    setCreateOpen(false);
    setActionError(null);
    announce("Work item created.");
  }

  async function updateItem(id: string, values: ItemFormValues, isCurrent: () => boolean): Promise<void> {
    await api<WorkItem>(`/api/items/${id}`, {
      method: "PATCH",
      body: valuesToPayload(values),
    });
    if (!isCurrent()) return;
    items.reload();
    setEditingId(null);
    setActionError(null);
    announce("Work item updated.");
  }

  async function deleteItem(id: string): Promise<void> {
    const selection = selectionGeneration.current;
    const form = formGeneration.current;
    const deletion = ++deleteGeneration.current;
    const isCurrent = () => selectionGeneration.current === selection &&
      formGeneration.current === form && deleteGeneration.current === deletion;
    try {
      await api<null>(`/api/items/${id}`, { method: "DELETE" });
    } catch (err: unknown) {
      if (isCurrent()) {
        setConfirmingId(null);
        setActionError(readErrorMessage(err));
      }
      return;
    }
    if (!isCurrent()) return;
    items.reload();
    setConfirmingId(null);
    setActionError(null);
    announce("Work item deleted.");
  }

  if (me.loading) {
    return (
      <main aria-busy="true">
        <p>Loading workspaces…</p>
      </main>
    );
  }

  if (me.error) {
    return (
      <main>
        <p className="banner banner-error" role="alert">
          {me.error}
        </p>
      </main>
    );
  }

  if (!me.data) {
    return null;
  }

  if (workspaces.length === 0) {
    return (
      <main>
        <p className="live-status" role="status">
          {live}
        </p>
        <CreateWorkspacePanel onCreate={createWorkspace} />
      </main>
    );
  }

  const itemList = items.data?.items ?? [];

  return (
    <main aria-busy={items.loading}>
      <p className="live-status" role="status">
        {live}
      </p>

      <section className="panel">
        <h2 style={{ fontSize: "1.05rem" }}>Workspace</h2>
        <div className="toolbar">
          <div className="field" style={{ marginBottom: 0 }}>
            <label htmlFor="workspace-select">Workspace</label>
            <select
              id="workspace-select"
              value={selectedId ?? ""}
              onChange={(e) => {
                changeSelection(e.target.value);
                setEditingId(null);
                setConfirmingId(null);
                setCreateOpen(false);
                setActionError(null);
              }}
            >
              {workspaces.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          {selected ? (
            <span className="muted">Your role: {ROLE_LABELS[selected.role] ?? selected.role}</span>
          ) : null}
          <button
            type="button"
            className="btn btn-primary"
            aria-expanded={createOpen}
            onClick={() => {
              formGeneration.current += 1;
              setCreateOpen((open) => !open);
              setEditingId(null);
            }}
          >
            {createOpen ? "Close new item form" : "New work item"}
          </button>
        </div>
      </section>

      {createOpen ? (
        <section className="panel" aria-labelledby="create-heading">
          <h2 id="create-heading" style={{ fontSize: "1.05rem" }}>
            New work item
          </h2>
          <ItemForm
            key="create"
            submitLabel="Create work item"
            busyLabel="Creating…"
            onSubmit={createItem}
            startAction={startFormAction}
            onCancel={() => {
              formGeneration.current += 1;
              setCreateOpen(false);
            }}
          />
        </section>
      ) : null}

      {actionError ? (
        <p className="banner banner-error" role="alert">
          {actionError}
        </p>
      ) : null}

      <section aria-labelledby="items-heading">
        <h2 id="items-heading" style={{ fontSize: "1.05rem" }}>
          Work items
        </h2>
        {items.loading && itemList.length === 0 ? <p>Loading work items…</p> : null}
        {items.error ? (
          <>
            <p className="banner banner-error" role="alert">
              {items.error}
            </p>
            <button type="button" className="btn" onClick={() => items.reload()}>
              Retry
            </button>
          </>
        ) : null}
        {!items.loading && !items.error && itemList.length === 0 ? (
          <p className="panel inline-note">
            No work items in this workspace yet. Use “New work item” to add the first one.
          </p>
        ) : null}
        <ul className="items" aria-label="Work items">
          {itemList.map((item) => (
            <li className="item-card" key={item.id} data-item-id={item.id}>
              {editingId === item.id ? (
                <ItemForm
                  key={`edit-${item.id}`}
                  initial={{
                    title: item.title,
                    notes: item.notes,
                    status: item.status,
                    dueDate: item.dueDate ?? "",
                  }}
                  submitLabel="Save changes"
                  busyLabel="Saving…"
                  onSubmit={(values, isCurrent) => updateItem(item.id, values, isCurrent)}
                  startAction={startFormAction}
                  onCancel={() => {
                    formGeneration.current += 1;
                    setEditingId(null);
                  }}
                />
              ) : (
                <>
                  <div className="item-head">
                    <h3>{item.title}</h3>
                    <StatusPill status={item.status} />
                  </div>
                  <p className="item-meta">
                    Updated {item.updatedAt.slice(0, 10)} ·{" "}
                    {item.dueDate ? `Due ${item.dueDate}` : "No due date"}
                  </p>
                  {item.notes ? <p className="item-notes">{item.notes}</p> : null}
                  <div className="item-actions">
                    {confirmingId === item.id ? (
                      <>
                        <button
                          type="button"
                          className="btn btn-danger"
                          aria-label={`Confirm delete ${item.title}`}
                          onClick={() => {
                            void deleteItem(item.id);
                          }}
                        >
                          Confirm delete
                        </button>
                        <button
                          type="button"
                          className="btn"
                          onClick={() => {
                            deleteGeneration.current += 1;
                            setConfirmingId(null);
                          }}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          type="button"
                          className="btn"
                          aria-label={`Edit ${item.title}`}
                          onClick={() => {
                            formGeneration.current += 1;
                            setEditingId(item.id);
                            setCreateOpen(false);
                          }}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="btn btn-danger"
                          aria-label={`Delete ${item.title}`}
                          onClick={() => {
                            deleteGeneration.current += 1;
                            setConfirmingId(item.id);
                          }}
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </div>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

function CreateWorkspacePanel({ onCreate }: { onCreate: (name: string) => Promise<void> }) {
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <section className="panel" aria-labelledby="first-workspace-heading">
      <h2 id="first-workspace-heading">Create your first workspace</h2>
      <p className="muted">
        Work items live inside workspaces. You will be the owner of this one.
      </p>
      {error ? (
        <p className="banner banner-error" role="alert">
          {error}
        </p>
      ) : null}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setBusy(true);
          setError(null);
          onCreate(name)
            .catch((err: unknown) => {
              setError(readErrorMessage(err, "Creating the workspace failed."));
            })
            .finally(() => setBusy(false));
        }}
      >
        <div className="field">
          <label htmlFor="workspace-name">Workspace name</label>
          <input
            id="workspace-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? "Creating…" : "Create workspace"}
        </button>
      </form>
    </section>
  );
}
