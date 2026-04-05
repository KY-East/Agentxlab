import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import type { Discipline } from "../types";

export function useDisciplines() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [tree, setTree] = useState<Discipline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getDisciplines(user?.id)
      .then(setTree)
      .catch((err) =>
        setError(err instanceof Error ? err.message : t("canvas.loadFailed"))
      )
      .finally(() => setLoading(false));
  }, [user?.id, t]);

  return { tree, loading, error, refresh: () => {
    setLoading(true);
    api.getDisciplines(user?.id).then(setTree).catch(() => {}).finally(() => setLoading(false));
  }};
}
