import React from 'react';

const Results = ({ results }) => {
  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="results">
      <h2>Results</h2>
      {results.map((medicine, index) => (
        <div key={index} className="medicine-card">
          <div className="medicine-header">
            <h3>{medicine.Medicine_name}</h3>
            {medicine.Medicine_name_nepali && (
              <h3 className="nepali-text">{medicine.Medicine_name_nepali}</h3>
            )}
          </div>

          <div className="medicine-section">
            <h4>Uses / प्रयोग</h4>
            <div className="two-column">
              <div className="english">
                <p>{medicine.Uses}</p>
              </div>
              {medicine.Uses_nepali && (
                <div className="nepali">
                  <p className="nepali-text">{medicine.Uses_nepali}</p>
                </div>
              )}
            </div>
          </div>

          <div className="medicine-section">
            <h4>Side Effects / साइड इफेक्ट</h4>
            <div className="two-column">
              <div className="english">
                <ul>
                  {medicine.Side_effects && medicine.Side_effects.map((effect, idx) => (
                    <li key={idx}>{effect}</li>
                  ))}
                </ul>
              </div>
              {medicine.Side_effects_nepali && medicine.Side_effects_nepali.length > 0 && (
                <div className="nepali">
                  <ul className="nepali-text">
                    {medicine.Side_effects_nepali.map((effect, idx) => (
                      <li key={idx}>{effect}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {medicine.match_score && (
            <div className="match-score">
              <small>Match Score: {(medicine.match_score * 100).toFixed(0)}%</small>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Results;
