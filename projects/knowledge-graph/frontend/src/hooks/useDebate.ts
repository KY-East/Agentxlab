import { useEffect, useState, useCallback } from "react";
import { api } from "../api/client";
import type { Debate } from "../types";

export function useDebate(debateId: number | null) {
  const [debate, setDebate] = useState<Debate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (debateId === null) {
      setDebate(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const d = await api.getDebate(debateId);
      setDebate(d);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载辩论失败");
    } finally {
      setLoading(false);
    }
  }, [debateId]);

  useEffect(() => {
    load();
  }, [load]);

  return { debate, setDebate, loading, error, reload: load };
}
