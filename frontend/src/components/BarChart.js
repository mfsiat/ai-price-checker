import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";

// Register chart components
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend, Title);

const BarChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const data = {
    labels: results.map((item) => item.provider),
    datasets: [
      {
        label: "Monthly Cost ($)",
        data: results.map((item) => item.monthly_cost),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#8AFF33",
          "#AA33FF",
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Monthly Cost per Provider" },
    },
  };

  return <Bar data={data} options={options} />;
};

export default BarChart;
