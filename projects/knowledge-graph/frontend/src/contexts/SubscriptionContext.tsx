import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { api } from "../api/client";
import { useAuth } from "./AuthContext";
import type { SubscriptionInfo } from "../types";

interface SubContextValue {
  sub: SubscriptionInfo | null;
  loading: boolean;
  refresh: () => Promise<void>;
  showUpgradePrompt: boolean;
  setShowUpgradePrompt: (v: boolean) => void;
}

const SubContext = createContext<SubContextValue>({
  sub: null,
  loading: false,
  refresh: async () => {},
  showUpgradePrompt: false,
  setShowUpgradePrompt: () => {},
});

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [sub, setSub] = useState<SubscriptionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);

  const refresh = useCallback(async () => {
    if (!user) {
      setSub(null);
      return;
    }
    setLoading(true);
    try {
      const res = await api.getMySubscription();
      setSub(res);
    } catch {
      setSub(null);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const handler = () => {
      setShowUpgradePrompt(true);
      refresh();
    };
    window.addEventListener("axl:quota-exceeded", handler);
    return () => window.removeEventListener("axl:quota-exceeded", handler);
  }, [refresh]);

  return (
    <SubContext.Provider value={{ sub, loading, refresh, showUpgradePrompt, setShowUpgradePrompt }}>
      {children}
    </SubContext.Provider>
  );
}

export function useSubscription() {
  return useContext(SubContext);
}
