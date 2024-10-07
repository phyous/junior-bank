import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Settings.css';

interface SettingsProps {
  userId: number;
}

const Settings: React.FC<SettingsProps> = ({ userId }) => {
  const navigate = useNavigate();
  const [interestRate, setInterestRate] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAccountData();
  }, [userId]);

  const fetchAccountData = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/account/${userId}`);
      setInterestRate((response.data.interest_rate * 100).toFixed(2));
    } catch (error) {
      console.error('Error fetching account data:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.put(`http://localhost:8000/account/${userId}/interest_rate`, {
        interest_rate: parseFloat(interestRate) / 100,
      });
      navigate('/dashboard');
    } catch (error) {
      setError('Error updating interest rate');
    }
  };

  return (
    <div className="settings-container">
      <h2>Account Settings</h2>
      <form className="settings-form" onSubmit={handleSubmit}>
        <label htmlFor="interestRate">Interest Rate (%)</label>
        <input
          type="number"
          id="interestRate"
          step="0.01"
          min="0"
          max="100"
          value={interestRate}
          onChange={(e) => setInterestRate(e.target.value)}
          required
        />
        <button type="submit">Update Interest Rate</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      <button className="back-button" onClick={() => navigate('/dashboard')}>
        Back to Dashboard
      </button>
    </div>
  );
};

export default Settings;