import { useMemo, useState } from 'react';
import { Table, Form, InputGroup } from 'react-bootstrap';

const RamTable = ({ rams, onRowClick }) => {
  const [filter, setFilter] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'latest_price', direction: 'ascending' });

  const filteredRams = useMemo(() => {
    let searchableRams = [...rams];
    if (filter) {
      searchableRams = searchableRams.filter((ram) =>
        ram.name_raw.toLowerCase().includes(filter.toLowerCase())
      );
    }
    return searchableRams;
  }, [rams, filter]);

  const sortedRams = useMemo(() => {
    let sortableRams = [...filteredRams];
    if (sortConfig.key !== null) {
      sortableRams.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableRams;
  }, [filteredRams, sortConfig]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getSortIndicator = (key) => {
    if (sortConfig.key === key) {
      return sortConfig.direction === 'ascending' ? ' ▲' : ' ▼';
    }
    return '';
  };

  return (
    <>
      <InputGroup className="mb-3">
        <InputGroup.Text>Search</InputGroup.Text>
        <Form.Control
          placeholder="Filter by name..."
          onChange={(e) => setFilter(e.target.value)}
        />
      </InputGroup>

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th onClick={() => requestSort('brand')}>Brand{getSortIndicator('brand')}</th>
            <th onClick={() => requestSort('name_raw')}>Name{getSortIndicator('name_raw')}</th>
            <th onClick={() => requestSort('capacity')}>Capacity{getSortIndicator('capacity')}</th>
            <th onClick={() => requestSort('speed')}>Speed{getSortIndicator('speed')}</th>
            <th onClick={() => requestSort('latency')}>Latency{getSortIndicator('latency')}</th>
            <th onClick={() => requestSort('latest_price')}>Price (NT$){getSortIndicator('latest_price')}</th>
            <th onClick={() => requestSort('latest_status')}>Status{getSortIndicator('latest_status')}</th>
            <th onClick={() => requestSort('latest_scraped_at')}>Last Updated{getSortIndicator('latest_scraped_at')}</th>
          </tr>
        </thead>
        <tbody>
          {sortedRams.map((ram) => (
            <tr key={ram.id} onClick={() => onRowClick(ram)}>
              <td>{ram.brand}</td>
              <td>{ram.name_raw}</td>
              <td>{ram.capacity}</td>
              <td>{ram.speed}</td>
              <td>{ram.latency}</td>
              <td>{ram.latest_price ? ram.latest_price.toLocaleString() : 'N/A'}</td>
              <td>{ram.latest_status}</td>
              <td>{new Date(ram.latest_scraped_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};

export default RamTable;
