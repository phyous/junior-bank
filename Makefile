# Makefile for Bank Account App

# Variables
PYTHON = python3
POETRY = poetry
NPM = npm
UVICORN = poetry run uvicorn

# Directories
CURRENT_DIR := $(shell pwd)
BACKEND_DIR := $(CURRENT_DIR)/backend
FRONTEND_DIR := $(CURRENT_DIR)/frontend

# Check if npm is installed
NPM_INSTALLED := $(shell command -v npm 2> /dev/null)

# Check the operating system
UNAME_S := $(shell uname -s)

# Phony targets
.PHONY: install install-backend install-frontend install-npm run run-backend run-frontend stop clean setup-frontend

# Default target
all: install run

# Install all dependencies
install: install-npm install-backend install-frontend

# Install npm if not present
install-npm:
ifndef NPM_INSTALLED
	@echo "npm not found. Installing npm..."
ifeq ($(UNAME_S),Linux)
	@sudo apt-get update && sudo apt-get install -y nodejs npm
else ifeq ($(UNAME_S),Darwin)
	@brew install node
else
	@echo "Unsupported operating system. Please install npm manually."
	@exit 1
endif
endif

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	@(cd $(BACKEND_DIR) && $(POETRY) install --no-root)

# Install frontend dependencies
install-frontend: install-npm setup-frontend
	@echo "Installing frontend dependencies..."
	@(cd $(FRONTEND_DIR) && $(NPM) install)

# Run the application (backend and frontend)
run: stop run-backend run-frontend

# Run the backend server
run-backend:
	@echo "Starting backend server..."
	@(cd $(BACKEND_DIR) && $(POETRY) run uvicorn main:app --reload --port 8000 &)

# Run the frontend development server
run-frontend: install-npm setup-frontend
	@echo "Starting frontend development server..."
	@(cd $(FRONTEND_DIR) && $(NPM) start)

# Stop the application
stop:
	@echo "Stopping servers..."
	@pkill -f uvicorn || true
	@pkill -f "node.*react-scripts" || true

# Clean up
clean: stop
	@echo "Cleaning up..."
	@(cd $(FRONTEND_DIR) && rm -rf node_modules build)
	@(cd $(BACKEND_DIR) && $(POETRY) env remove --all)
	@find $(CURRENT_DIR) -type d -name __pycache__ -exec rm -rf {} +
	@find $(CURRENT_DIR) -type f -name '*.pyc' -delete

# Setup frontend structure
setup-frontend:
	@echo "Setting up frontend structure..."
	@mkdir -p $(FRONTEND_DIR)/public $(FRONTEND_DIR)/src
	@echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Bank Account App</title></head><body><div id="root"></div></body></html>' > $(FRONTEND_DIR)/public/index.html
	@echo 'import React from "react"; import ReactDOM from "react-dom"; import "./index.css"; import App from "./App"; ReactDOM.render(<React.StrictMode><App /></React.StrictMode>,document.getElementById("root"));' > $(FRONTEND_DIR)/src/index.tsx
	@echo 'body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; } code { font-family: source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace; }' > $(FRONTEND_DIR)/src/index.css