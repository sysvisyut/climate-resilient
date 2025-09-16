"use client";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Scatter } from "react-chartjs-2";
import { useEffect } from "react";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

type Props = {
  labels: string[];
  temps: number[];
  risk7: number[];
};

export default function TrendCharts({ labels, temps, risk7 }: Props) {
  useEffect(() => {
    (async () => {
      const mod = await import("chartjs-plugin-zoom");
      // @ts-ignore
      if (mod && mod.default) {
        // @ts-ignore - runtime registration only in browser
        ChartJS.register(mod.default);
      }
    })();
  }, []);
  const lineData = {
    labels,
    datasets: [
      { label: "Temperature (°C)", data: temps, borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,0.2)", tension: 0.35, fill: true },
      { label: "Risk (scaled)", data: risk7.map((r) => r * 50), borderColor: "#dc2626", backgroundColor: "rgba(220,38,38,0.2)", tension: 0.35, fill: true },
    ],
  };
  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false as const,
    plugins: { legend: { position: "top" as const }, zoom: { zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: "x" as const } } },
    scales: { y: { grid: { color: "rgba(0,0,0,0.05)" } }, x: { grid: { display: false } } },
  };

  const scatterData = {
    datasets: [
      { label: "Temp vs Risk", data: temps.map((t, i) => ({ x: t, y: risk7[i] })), backgroundColor: "#10b981" },
    ],
  };
  const scatterOptions = { responsive: true, maintainAspectRatio: false as const, scales: { x: { title: { display: true, text: "Temp (°C)" } }, y: { title: { display: true, text: "Risk" } } } };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="card p-6 h-72">
        <h3 className="font-semibold mb-3">7-day Temperature & Risk</h3>
        <Line data={lineData} options={lineOptions} aria-label="Temperature and Risk Line Chart" />
      </div>
      <div className="card p-6 h-72">
        <h3 className="font-semibold mb-3">Temp vs Risk</h3>
        <Scatter data={scatterData} options={scatterOptions} aria-label="Temperature vs Risk Scatter Chart" />
      </div>
    </div>
  );
}


