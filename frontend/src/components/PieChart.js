import React from "react";
import { Pie } from "react-chartjs-2";

const PieChart = ({ results }) => {
  if (!results || results.length === 0) return null;

  const colors = [
    "#FF6384","#36A2EB","#FFCE56","#8AFF33",
    "#AA33FF","#FF8C00","#00CED1","#FF1493"
  ];

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
