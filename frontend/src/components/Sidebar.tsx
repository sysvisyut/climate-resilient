"use client";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";

type NavItem = { key: string; label: string };

function getNav(role: string | null): NavItem[] {
  if (role === "Admin") return [
    { key: "overview", label: "Overview" },
    { key: "patients", label: "Patients" },
    { key: "resources", label: "Resources" },
    { key: "alerts", label: "Alerts" },
    { key: "reports", label: "Reports" },
    { key: "settings", label: "Settings" },
  ];
  if (role === "Clinician") return [
    { key: "overview", label: "Overview" },
    { key: "patients", label: "Patients" },
    { key: "alerts", label: "Alerts" },
  ];
  if (role === "Analyst") return [
    { key: "overview", label: "Overview" },
    { key: "reports", label: "Reports" },
  ];
  return [{ key: "overview", label: "Overview" }];
}

type Props = {
  selected: string;
  onSelect: (key: string) => void;
};

export default function Sidebar({ selected, onSelect }: Props) {
  const { role, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const items = getNav(role);

  return (
    <aside className="md:w-64 w-full md:h-auto">
      <div className="md:hidden flex justify-between items-center mb-3">
        <button className="px-3 py-2 rounded-md border" onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-controls="mobile-nav">Menu</button>
        <button className="px-3 py-2 rounded-md border" onClick={logout}>Logout</button>
      </div>
      <nav id="mobile-nav" className={`md:block ${open ? "block" : "hidden"}`} aria-label="Sidebar">
        <ul className="space-y-1">
          {items.map((it) => (
            <li key={it.key}>
              <button
                className={`w-full text-left px-3 py-2 rounded-md ${selected === it.key ? "bg-blue-600 text-white" : "bg-white text-gray-800 border"}`}
                onClick={() => { onSelect(it.key); setOpen(false); }}
              >
                {it.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}


