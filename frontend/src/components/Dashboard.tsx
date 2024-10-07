import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TransactionModal from './TransactionModal';
import './Dashboard.css';

interface DashboardProps {
  userId: number;
  onLogout: () => void;
}

interface Account {
  id: number;
  balance: number;
  interest_rate: number;
}

interface Transaction {
  id: number;
  amount: number;
  transaction_type: string;
  note: string;
  timestamp: string;
}

const Dashboard: React.FC<DashboardProps> = ({ userId, onLogout }) => {
  const navigate = useNavigate();
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchAccountData();
  }, [userId]);

  useEffect(() => {
    if (account) {
      fetchTransactions();
    }
  }, [account]);

  const fetchAccountData = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/account/${userId}`);
      setAccount(response.data);
    } catch (error) {
      console.error('Error fetching account data:', error);
    }
  };

  const fetchTransactions = async () => {
    if (account) {
      try {
        const response = await axios.get(`http://localhost:8000/transactions/${account.id}`);
        const sortedTransactions = response.data.sort((a: Transaction, b: Transaction) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        setTransactions(sortedTransactions);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    }
  };

  const handleNewTransaction = async (amount: number, type: string, note: string) => {
    if (account) {
      try {
        await axios.post('http://localhost:8000/transaction', {
          account_id: account.id,
          amount: type === 'withdrawal' ? -amount : amount,
          transaction_type: type,
          note: note,
        });
        await fetchAccountData();
        await fetchTransactions();
      } catch (error) {
        console.error('Error creating transaction:', error);
      }
    }
  };

  const handleSettingsClick = () => {
    navigate('/settings');
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <div>
          <button className="settings-button" onClick={handleSettingsClick}>
            ⚙️ Settings
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
      {account && (
        <div className="account-info">
          <h3>Account Balance</h3>
          <div className="balance-amount">${account.balance.toFixed(2)}</div>
          <p>Interest Rate: {(account.interest_rate * 100).toFixed(2)}%</p>
        </div>
      )}
      <button className="new-transaction-btn" onClick={() => setIsModalOpen(true)}>New Transaction</button>
      <div className="transactions-list">
        <h3>Transactions</h3>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td>{new Date(transaction.timestamp).toLocaleString()}</td>
                <td>{transaction.transaction_type}</td>
                <td>${Math.abs(transaction.amount).toFixed(2)}</td>
                <td>{transaction.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <TransactionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleNewTransaction}
      />
    </div>
  );
};

export default Dashboard;