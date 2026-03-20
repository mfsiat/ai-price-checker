import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const BarChart = ({ results }) => {
  if (!results || results.length === 0) return <p>No data</p>;

  const data = {
    labels: results.map(
      (item) => `${item.provider} (${item.model})`
    ),
    datasets: [
      {
        label: "Monthly Cost ($)",
        data: results.map((item) => item.monthly_cost),
      },
    ],
  };

  return <Bar data={data} />;
};

export default BarChart;