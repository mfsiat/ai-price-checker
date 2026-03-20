import { Pie } from "react-chartjs-2";

const PieChart = ({ results }) => {
  if (!results || results.length === 0) return <p>No data</p>;

  const data = {
    labels: results.map((item) => item.provider),
    datasets: [
      {
        data: results.map((item) => item.monthly_cost),
      },
    ],
  };

  return <Pie data={data} />;
};

export default PieChart;