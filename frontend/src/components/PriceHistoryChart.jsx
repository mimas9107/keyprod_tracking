import { useEffect, useState } from 'react';
import { Modal, Spinner, Alert } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { fetchRamChartData } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const PriceHistoryChart = ({ ram, show, onHide }) => {
  const [chartData, setChartData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (ram && show) {
      const loadChartData = async () => {
        setIsLoading(true);
        setError('');
        setChartData(null);
        try {
          const data = await fetchRamChartData(ram.id);
          setChartData({
            labels: data.dates,
            datasets: [
              {
                label: 'Price History (NT$)',
                data: data.prices,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
              },
            ],
          });
        } catch (err) {
          setError(err.message || 'Could not load chart data.');
        } finally {
          setIsLoading(false);
        }
      };
      loadChartData();
    }
  }, [ram, show]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: ram ? ram.name_raw : 'Price History',
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function (value) {
            return 'NT$ ' + value;
          },
        },
      },
    },
  };

  return (
    <Modal show={show} onHide={onHide} size="xl" centered>
      <Modal.Header closeButton>
        <Modal.Title>{ram ? ram.name_raw : 'Loading...'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoading && <div className="text-center"><Spinner animation="border" /></div>}
        {error && <Alert variant="danger">{error}</Alert>}
        {chartData && <Line options={options} data={chartData} />}
      </Modal.Body>
    </Modal>
  );
};

export default PriceHistoryChart;
