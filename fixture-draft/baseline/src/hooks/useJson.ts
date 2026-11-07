import { useCallback, useEffect, useState } from "react";
import { api, readErrorMessage } from "../api-client.js";

export interface UseJsonResult<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

/** Small fetch hook with manual reload. `null` path = do not fetch. */
export function useJson<T>(path: string | null): UseJsonResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(path !== null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (path === null) {
      setData(null);
      setError(null);
      setLoading(false);
      return;
    }
    let alive = true;
    setLoading(true);
    api<T>(path)
      .then((payload) => {
        if (alive) {
          setData(payload);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (alive) {
          setError(readErrorMessage(err));
        }
      })
      .finally(() => {
        if (alive) {
          setLoading(false);
        }
      });
    return () => {
      alive = false;
    };
  }, [path, tick]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { data, error, loading, reload };
}
