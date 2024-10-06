# Junior Bank

Junior Bank is a simple banking application designed to help young people learn about managing finances. 
It provides basic banking functionalities in a user-friendly interface.

## Features

- User registration and login
- Account balance viewing
- Deposit and withdrawal transactions
- Transaction history
- Daily interest calculation

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Run the FastAPI server:
   ```
   poetry run uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```

4. Open your browser and visit `http://localhost:3000` to use the application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

