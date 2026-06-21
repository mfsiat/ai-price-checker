import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import chartColors from "../chartColors";

ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const colors = chartColors;

  const data = {
    labels: results.map((item) => item.provider),
    datasets: [
      {
        data: results.map((item) => item.monthly_cost),
        backgroundColor: results.map((_, i) => colors[i % colors.length]),
      },
    ],
  };

  const options = {
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            const item = results[context.dataIndex];
            return `${item.provider} (${item.model}): $${item.monthly_cost}`;
          },
        },
      },
    },
  };

  return <Pie data={data} options={options} />;
};

export default PieChart;
