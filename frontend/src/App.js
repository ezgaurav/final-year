import React, { useState, useEffect } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import ImageUpload from './components/ImageUpload';
import Camera from './components/Camera';
import Results from './components/Results';
import api from './services/api';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDemo, setShowDemo] = useState(false);

  const handleResults = (data) => {
    setResults(data);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  const loadDemoData = async () => {
    setLoading(true);
    try {
      const response = await api.getDemoData();
      if (response.success) {
        setResults([response.medicine]);
        setShowDemo(true);
      }
    } catch (error) {
      console.error('Demo error:', error);
      // Fallback demo data
      setResults([{
        Medicine_name: "Paracetamol 500mg Tablet",
        Medicine_name_nepali: "पारासिटामोल ५००mg ट्याब्लेट",
        Uses: "Treatment of Fever, Pain relief",
        Uses_nepali: "ज्वरोको उपचार, पीडा राहत",
        Side_effects: ["Nausea", "Vomiting", "Stomach pain", "Dark urine", "Fatigue"],
        Side_effects_nepali: ["वाकवाकी", "बान्ता", "पेट दुखाइ", "अँध्यारो पिसाब", "थकान"]
      }]);
      setShowDemo(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏥 Medicine Detection AI</h1>
        <p className="subtitle">Detect medicines and get information in English & Nepali</p>
      </header>

      <main className="App-main">
        <div className="controls">
          <SearchBar onResults={handleResults} onLoading={handleLoading} />
          
          <div className="button-group">
            <ImageUpload onResults={handleResults} onLoading={handleLoading} />
            <Camera onResults={handleResults} onLoading={handleLoading} />
            <button onClick={loadDemoData} className="demo-button">
              🎯 Try Demo
            </button>
          </div>
        </div>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {showDemo && (
          <div className="demo-notice">
            <p>📌 This is demo data (Paracetamol)</p>
          </div>
        )}

        <Results results={results} />

        <div className="instructions">
          <h3>How to Use</h3>
          <ol>
            <li><strong>Search:</strong> Type medicine name in the search bar</li>
            <li><strong>Upload:</strong> Click "Upload Image" to detect from a photo</li>
            <li><strong>Camera:</strong> Click "Use Camera" to capture medicine photo</li>
            <li><strong>Demo:</strong> Click "Try Demo" to see sample data</li>
          </ol>
          <p className="note">
            All results are displayed in both English and Nepali (नेपाली)
          </p>
        </div>
      </main>

      <footer className="App-footer">
        <p>Medicine Detection AI - Final Year Project</p>
      </footer>
    </div>
  );
}

export default App;
