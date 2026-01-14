import { useState, useEffect } from 'react';
import { Container, Spinner, Alert } from 'react-bootstrap';
import { fetchRamOptions } from './services/api';
import RamTable from './components/RamTable';
import PriceHistoryChart from './components/PriceHistoryChart';
import './App.css';

function App() {
  const [rams, setRams] = useState([]);
  const [selectedRam, setSelectedRam] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadRamOptions = async () => {
      try {
        setIsLoading(true);
        const data = await fetchRamOptions();
        setRams(data);
      } catch (err) {
        setError(err.message || 'Failed to load RAM data. Make sure the backend server is running.');
      } finally {
        setIsLoading(false);
      }
    };
    loadRamOptions();
  }, []);

  const handleRowClick = (ram) => {
    setSelectedRam(ram);
  };

  const handleModalClose = () => {
    setSelectedRam(null);
  };

  return (
    <Container fluid>
      <h1 className="my-4 text-center">RAM Price Tracker</h1>
      
      {isLoading && (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p>Loading data...</p>
        </div>
      )}

      {error && (
        <Alert variant="danger" className="text-center">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {!isLoading && !error && (
        <RamTable rams={rams} onRowClick={handleRowClick} />
      )}

      {selectedRam && (
        <PriceHistoryChart
          ram={selectedRam}
          show={selectedRam !== null}
          onHide={handleModalClose}
        />
      )}
    </Container>
  );
}

export default App;
