"use client";
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { mockUsers } from "@/data/mockUsers";

export type UserRole = "Admin" | "Clinician" | "Analyst";

type Session = {
  username: string;
  role: UserRole;
};

type AuthContextType = {
  isAuthenticated: boolean;
  role: UserRole | null;
  username: string | null;
  login: (username: string, password: string) => boolean;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("crhs_session");
      if (raw) setSession(JSON.parse(raw));
    } catch {}
  }, []);

  const login = (username: string, password: string) => {
    const found = mockUsers.find((u) => u.username === username && u.password === password);
    if (!found) return false;
    const nextSession: Session = { username: found.username, role: found.role };
    setSession(nextSession);
    try {
      localStorage.setItem("crhs_session", JSON.stringify(nextSession));
    } catch {}
    return true;
  };

  const logout = () => {
    setSession(null);
    try {
      localStorage.removeItem("crhs_session");
    } catch {}
  };

  const value = useMemo<AuthContextType>(() => ({
    isAuthenticated: !!session,
    role: session?.role ?? null,
    username: session?.username ?? null,
    login,
    logout,
  }), [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};


