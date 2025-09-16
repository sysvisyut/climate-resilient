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
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

type Props = {
  labels: string[];
  data: number[];
};

export default function TemperatureChart({ labels, data }: Props) {
  const dataset = {
    labels,
    datasets: [
      {
        label: "Temperature (°C)",
        data,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.2)",
        tension: 0.35,
        pointRadius: 3,
        fill: true,
      },
    ],
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false as const,
    plugins: {
      legend: { display: true, position: "top" as const },
      title: { display: false, text: "Temperature (°C)" },
    },
    scales: {
      y: { grid: { color: "rgba(0,0,0,0.05)" } },
      x: { grid: { display: false } },
    },
  };

  return (
    <div className="h-64 sm:h-72 md:h-80 lg:h-96">
      <Line data={dataset} options={options} />
    </div>
  );
}


