import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Signup.css';

interface SignupProps {
  onSignup: (id: number) => void;
}

const Signup: React.FC<SignupProps> = ({ onSignup }) => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [interestRate, setInterestRate] = useState('1.00');
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);

  const handleInitialSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password) {
      try {
        // Check if username already exists
        await axios.get(`http://localhost:8000/check_username/${username}`);
        setStep(2);
      } catch (error: any) {
        if (error.response && error.response.status === 400) {
          setError('Username already exists');
        } else {
          setError('An error occurred. Please try again.');
        }
      }
    } else {
      setError('Please fill in all fields');
    }
  };

  const handleFinalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/signup', {
        username,
        password,
        interest_rate: parseFloat(interestRate) / 100,
      });
      onSignup(response.data.id);
      navigate('/dashboard');
    } catch (error) {
      setError('Error creating account');
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      {step === 1 ? (
        <form className="signup-form" onSubmit={handleInitialSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Next</button>
        </form>
      ) : (
        <form className="signup-form" onSubmit={handleFinalSubmit}>
          <div className="interest-rate-explanation">
            <p>Set your account's interest rate. This rate determines how much interest your account will earn daily.</p>
            <p>You can set any rate between 0% and 100%, up to two decimal places.</p>
          </div>
          <input
            type="number"
            step="0.01"
            min="0"
            max="100"
            placeholder="Interest Rate (%)"
            value={interestRate}
            onChange={(e) => setInterestRate(e.target.value)}
            required
          />
          <button type="submit">Sign Up</button>
        </form>
      )}
      {error && <p className="error-message">{error}</p>}
      <p className="login-link">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

export default Signup;