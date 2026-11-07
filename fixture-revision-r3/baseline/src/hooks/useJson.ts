import { useCallback, useEffect, useState } from "react";
import { api, readErrorMessage } from "../api-client.js";

export interface UseJsonResult<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

interface RequestState<T> {
  /** The path the stored data/error belongs to. */
  path: string | null;
  data: T | null;
  error: string | null;
  loading: boolean;
}

/**
 * Small fetch hook with manual reload. `null` path = do not fetch.
 *
 * Data is keyed by request path: when `path` changes, the previous
 * path's data and error are never exposed for the new path — during the
 * switch the hook reports `data: null` + `loading: true`, and a failed
 * load for the new path clears the old workspace's data as well
 * (`data: null` + `error`), so stale cross-workspace items or actions
 * can never render (baseline contract §6). Refetches of the *same* path
 * (via `reload`) keep the previously loaded data visible while loading.
 */
export function useJson<T>(path: string | null): UseJsonResult<T> {
  const [state, setState] = useState<RequestState<T>>({
    path,
    data: null,
    error: null,
    loading: path !== null,
  });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (path === null) {
      setState({ path: null, data: null, error: null, loading: false });
      return;
    }
    let alive = true;
    setState((prev) => ({
      path,
      data: prev.path === path ? prev.data : null,
      error: null,
      loading: true,
    }));
    api<T>(path)
      .then((payload) => {
        if (alive) {
          setState({ path, data: payload, error: null, loading: false });
        }
      })
      .catch((err: unknown) => {
        if (alive) {
          setState((prev) => ({
            path,
            // Same-path refetch failure keeps the previously loaded data
            // (it still belongs to this workspace); a switch to a new path
            // clears it so no other workspace's data survives the failure.
            data: prev.path === path ? prev.data : null,
            error: readErrorMessage(err),
            loading: false,
          }));
        }
      })
    return () => {
      alive = false;
    };
  }, [path, tick]);

  // Derived view for the render between a path change and the effect run:
  // data/error of the previous path are never surfaced for the new one.
  const view =
    state.path === path
      ? state
      : { path, data: null, error: null, loading: path !== null };

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { data: view.data, error: view.error, loading: view.loading, reload };
}
