import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
  type ChartData,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

// Register Chart.js components only when this component is loaded
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface TrendsChartProps {
  data: ChartData<'bar' | 'line'>;
  options: ChartOptions<'bar' | 'line'>;
  type: 'bar' | 'line';
}

const TrendsChart = ({ data, options, type }: TrendsChartProps) => {
  return (
    <div className="w-full h-full">
      {type === 'bar' ? (
        <Bar data={data} options={options} />
      ) : (
        <Line data={data} options={options} />
      )}
    </div>
  );
};

export default TrendsChart;
