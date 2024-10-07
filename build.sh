#!/bin/bash

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..

# Start the backend server
python backend/main.py