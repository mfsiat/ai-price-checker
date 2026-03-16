import React from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";

// Register chart components
ChartJS.register(ArcElement, Tooltip, Legend, Title);

const PieChart = ({ results }) => {
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
        borderColor: "#fff",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "bottom" },
      title: { display: true, text: "AI Tools Monthly Cost Comparison" },
    },
  };

  return (
    <div style={{ maxWidth: "500px", marginTop: "40px" }}>
      <Pie data={data} options={options} />
    </div>
  );
};

export default PieChart;
