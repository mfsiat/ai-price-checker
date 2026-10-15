import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import chartColors from "../chartColors";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const cssVar = (name) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const BarChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const colors = chartColors;
  const textColor = cssVar("--text-muted") || "#646a85";
  const gridColor = cssVar("--border") || "#e6e8f0";

  const data = {
    labels: results.map((item) => `${item.provider} (${item.model})`),
    datasets: [
      {
        label: "Monthly Cost ($)",
        data: results.map((item) => item.monthly_cost),
        backgroundColor: results.map((_, i) => colors[i % colors.length]),
        borderRadius: 6,
        maxBarThickness: 48,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        ticks: { color: textColor },
        grid: { display: false },
      },
      y: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default BarChart;
