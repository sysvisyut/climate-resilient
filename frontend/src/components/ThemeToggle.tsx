"use client";
import { useTheme } from "@/context/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button aria-label="Toggle theme" className="px-3 py-2 rounded-md border border-black/10 shadow-sm" onClick={toggle}>
      {theme === "light" ? "Light" : "Dark"}
    </button>
  );
}


