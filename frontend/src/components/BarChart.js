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

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const BarChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const colors = [
    "#FF6384","#36A2EB","#FFCE56","#8AFF33",
    "#AA33FF","#FF8C00","#00CED1","#FF1493"
  ];

  const data = {
    labels: results.map(
      (item) => `${item.provider} (${item.model})`
    ),
    datasets: [
      {
        label: "Monthly Cost ($)",
        data: results.map((item) => item.monthly_cost),
        backgroundColor: results.map((_, i) => colors[i % colors.length]),
      },
    ],
  };

  return <Bar data={data} />;
};

export default BarChart;
