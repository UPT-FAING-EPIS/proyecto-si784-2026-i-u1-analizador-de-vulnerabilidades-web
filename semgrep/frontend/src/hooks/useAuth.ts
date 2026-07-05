"use client";

import { useState, useEffect, useCallback } from "react";
import { authApi, type AuthUser } from "@/lib/api";

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    try {
      const me = await authApi.me();
      setUser(me);
    } catch {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchMe(); }, [fetchMe]);

  const login = async (username: string, password: string) => {
    const data = await authApi.login(username, password);
    localStorage.setItem("token", data.access_token);
    const me = await authApi.me();
    setUser(me);
    return data;
  };

  const register = async (username: string, email: string, password: string) => {
    const data = await authApi.register(username, email, password);
    localStorage.setItem("token", data.access_token);
    const me = await authApi.me();
    setUser(me);
    return data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return { user, loading, login, register, logout };
}
