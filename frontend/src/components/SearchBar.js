import React, { useState } from 'react';
import api from '../services/api';

const SearchBar = ({ onResults, onLoading }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    onLoading(true);
    try {
      const response = await api.searchMedicine(query);
      if (response.success) {
        onResults(response.results);
      } else {
        onResults([]);
        alert('No medicines found. Try a different search term.');
      }
    } catch (error) {
      console.error('Search error:', error);
      alert('Error searching medicines. Please try again.');
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch}>
        <div className="search-input-container">
          <input
            type="text"
            placeholder="Search medicine by name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            🔍 Search
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchBar;
