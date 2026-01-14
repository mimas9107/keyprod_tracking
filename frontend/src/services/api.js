// The base URL of the backend API.
// Make sure the backend server is running on this address.
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Fetches all RAM options with their latest prices.
 * @returns {Promise<Array>} A promise that resolves to an array of RAM options.
 */
export const fetchRamOptions = async () => {
  const response = await fetch(`${API_BASE_URL}/ram-options`);
  if (!response.ok) {
    throw new Error('Failed to fetch RAM options');
  }
  return response.json();
};

/**
 * Fetches the price history for a specific RAM option to be used in a chart.
 * @param {number} ramId The ID of the RAM option.
 * @returns {Promise<Object>} A promise that resolves to chart data (dates and prices).
 */
export const fetchRamChartData = async (ramId) => {
  const response = await fetch(`${API_BASE_URL}/ram/${ramId}/chart-data`);
  if (!response.ok) {
    throw new Error('Failed to fetch chart data');
  }
  return response.json();
};
