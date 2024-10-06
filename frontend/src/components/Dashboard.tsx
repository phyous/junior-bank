import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TransactionModal from './TransactionModal';

interface DashboardProps {
  userId: number;
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

const Dashboard: React.FC<DashboardProps> = ({ userId }) => {
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchAccountData();
    fetchTransactions();
  }, [userId]);

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
        setTransactions(response.data);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    }
  };

  const handleNewTransaction = async (amount: number, type: string) => {
    if (account) {
      try {
        await axios.post('http://localhost:8000/transaction', {
          account_id: account.id,
          amount: type === 'withdrawal' ? -amount : amount,
          transaction_type: type,
        });
        fetchAccountData();
        fetchTransactions();
      } catch (error) {
        console.error('Error creating transaction:', error);
      }
    }
  };

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      {account && (
        <div className="account-info">
          <h3>Account Balance: ${account.balance.toFixed(2)}</h3>
          <p>Interest Rate: {account.interest_rate}%</p>
        </div>
      )}
      <button onClick={() => setIsModalOpen(true)}>New Transaction</button>
      <div className="transactions-list">
        <h3>Transactions</h3>
        <ul>
          {transactions.map((transaction) => (
            <li key={transaction.id}>
              <span>{new Date(transaction.timestamp).toLocaleString()}</span>
              <span>{transaction.transaction_type}</span>
              <span>${Math.abs(transaction.amount).toFixed(2)}</span>
              <span>{transaction.note}</span>
            </li>
          ))}
        </ul>
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