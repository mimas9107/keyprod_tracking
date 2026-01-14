import { useMemo, useState } from 'react';
import { Card, Button, Form, InputGroup, Row, Col, Dropdown } from 'react-bootstrap';
import ReactPaginate from 'react-paginate';
import { addToTracking } from '../services/api';

const RamTable = ({ rams, onRowClick }) => {
  const [filter, setFilter] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'latest_price', direction: 'ascending' });
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 50;

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

  const pageCount = Math.ceil(sortedRams.length / itemsPerPage);
  const offset = currentPage * itemsPerPage;
  const currentRams = sortedRams.slice(offset, offset + itemsPerPage);

  const handlePageClick = (data) => {
    setCurrentPage(data.selected);
  };

  const handleAddToTracking = async (ramId) => {
    try {
      await addToTracking(ramId);
      alert(`Added RAM ${ramId} to tracking`);
      // Optionally, update the ram's is_tracked status here if needed
    } catch {
      alert('Failed to add to tracking');
    }
  };

  const handleSortChange = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  return (
    <>
      <InputGroup className="mb-3">
        <InputGroup.Text>Search</InputGroup.Text>
        <Form.Control
          placeholder="Filter by name..."
          onChange={(e) => setFilter(e.target.value)}
        />
        <Dropdown>
          <Dropdown.Toggle variant="outline-secondary" id="dropdown-sort">
            Sort by
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Dropdown.Item onClick={() => handleSortChange('brand')}>Brand</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('name_raw')}>Name</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('capacity')}>Capacity</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('speed')}>Speed</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('latency')}>Latency</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('latest_price')}>Price</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('latest_status')}>Status</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSortChange('latest_scraped_at')}>Last Updated</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </InputGroup>

      <div>
        {currentRams.map((ram) => (
          <Card key={ram.id} className="mb-2" onClick={() => onRowClick(ram)} style={{ cursor: 'pointer' }}>
            <Card.Body>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <div>{ram.brand} {ram.name_raw} - {ram.latest_price ? ram.latest_price.toLocaleString() : 'N/A'} NT$ ({ram.latest_status})</div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>{ram.capacity} {ram.speed} {ram.latency}</div>
                </div>
                <Button
                  variant="outline-primary"
                  size="sm"
                  disabled={ram.is_tracked}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAddToTracking(ram.id);
                  }}
                >
                  {ram.is_tracked ? 'Tracked' : 'Track'}
                </Button>
              </div>
            </Card.Body>
          </Card>
        ))}
      </div>

      <ReactPaginate
        previousLabel={'Previous'}
        nextLabel={'Next'}
        breakLabel={'...'}
        pageCount={pageCount}
        marginPagesDisplayed={2}
        pageRangeDisplayed={5}
        onPageChange={handlePageClick}
        containerClassName={'pagination justify-content-center'}
        pageClassName={'page-item'}
        pageLinkClassName={'page-link'}
        previousClassName={'page-item'}
        previousLinkClassName={'page-link'}
        nextClassName={'page-item'}
        nextLinkClassName={'page-link'}
        breakClassName={'page-item'}
        breakLinkClassName={'page-link'}
        activeClassName={'active'}
      />
    </>
  );
};

export default RamTable;
