# Makefile for Bank Account App

# Variables
PYTHON = python3
POETRY = poetry
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 3000
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
.PHONY: all install install-backend install-frontend install-npm run run-backend run-frontend stop clean setup-frontend build-frontend deploy migrate-backend test-integration

# Default target
all: deploy

# Install all dependencies
install: install-backend install-frontend

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
	@(cd $(BACKEND_DIR) && $(POETRY) install --no-root --no-interaction)

# Install frontend dependencies
install-frontend: install-npm setup-frontend
	@echo "Installing frontend dependencies..."
	@(cd $(FRONTEND_DIR) && $(NPM) install)

# Build frontend
build-frontend: install-frontend
	@echo "Building frontend for production..."
	@(cd $(FRONTEND_DIR) && REACT_APP_API_BASE_URL=http://localhost:$(BACKEND_PORT) $(NPM) run build)

# Migrate backend database
migrate-backend: install-backend
	@echo "Running database migrations..."
	@(cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head)

# Deploy the application (for general use)
deploy: stop migrate-backend build-frontend
	@echo "Starting backend server on port $(BACKEND_PORT)..."
	@(cd $(BACKEND_DIR) && $(UVICORN) main:app --host 0.0.0.0 --port $(BACKEND_PORT) &)
	@echo "Starting frontend server on port $(FRONTEND_PORT)..."
	@(cd $(FRONTEND_DIR)/build && $(PYTHON) -m http.server $(FRONTEND_PORT) &)
	@echo "Application deployed. Backend: http://localhost:$(BACKEND_PORT) Frontend: http://localhost:$(FRONTEND_PORT)"

# Run the application in development mode
run: stop run-backend run-frontend

# Run the backend server with auto-reload
run-backend:
	@echo "Starting backend server with auto-reload on port $(BACKEND_PORT)..."
	@(cd $(BACKEND_DIR) && $(UVICORN) main:app --reload --port $(BACKEND_PORT) &)

# Run the frontend development server
run-frontend: install-npm setup-frontend
	@echo "Starting frontend development server (typically on port 3000)..."
	@(cd $(FRONTEND_DIR) && REACT_APP_API_BASE_URL=http://localhost:$(BACKEND_PORT) $(NPM) start &)

# Run integration tests
test-integration: migrate-backend build-frontend
	@echo "Starting application for integration tests..."
	@echo "Starting backend server for tests on port $(BACKEND_PORT)..."
	@(cd $(BACKEND_DIR) && $(UVICORN) main:app --host 0.0.0.0 --port $(BACKEND_PORT) &)
	@echo "Starting frontend server for tests on port $(FRONTEND_PORT)..."
	@(cd $(FRONTEND_DIR)/build && $(PYTHON) -m http.server $(FRONTEND_PORT) &)
	@echo "Waiting for servers to start..."
	@sleep 10
	@echo "Running integration tests..."
	@trap '$(MAKE) stop || true' EXIT TERM INT; \
	(cd $(BACKEND_DIR) && $(POETRY) run env API_BASE_URL=http://localhost:$(BACKEND_PORT) FRONTEND_URL=http://localhost:$(FRONTEND_PORT) python -m unittest discover -s ../tests/integration -p 'test_*.py'; EXIT_CODE=$$?; \
	echo "Test execution finished with code $$EXIT_CODE."; \
	exit $$EXIT_CODE)
	@echo "Integration tests execution attempt finished (outside subshell)."
	@echo "Ensuring servers are stopped post-tests..."
	@$(MAKE) stop
	@echo "Test integration target finished."

# Stop the application (general stop for dev/manual deploy)
stop:
	@echo "Stopping servers..."
	@pkill -f "$(UVICORN) main:app --host 0.0.0.0 --port $(BACKEND_PORT)" || true
	@pkill -f "$(UVICORN) main:app --reload --port $(BACKEND_PORT)" || true
	@pkill -f "$(PYTHON) -m http.server $(FRONTEND_PORT)" || true
	@pkill -f "node.*react-scripts" || true

# Clean up
clean: stop
	@echo "Cleaning up..."
	@(cd $(FRONTEND_DIR) && rm -rf node_modules build)
	@(cd $(BACKEND_DIR) && $(POETRY) env remove --all || true)
	@find $(CURRENT_DIR) -type d -name __pycache__ -exec rm -rf {} +
	@find $(CURRENT_DIR) -type f -name '*.pyc' -delete

# Setup frontend structure
setup-frontend:
	@echo "Setting up frontend structure..."
	@mkdir -p $(FRONTEND_DIR)/public $(FRONTEND_DIR)/src
	@echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Bank Account App</title></head><body><div id="root"></div></body></html>' > $(FRONTEND_DIR)/public/index.html
	@echo 'import React from "react"; import ReactDOM from "react-dom"; import "./index.css"; import App from "./App"; ReactDOM.render(<React.StrictMode><App /></React.StrictMode>,document.getElementById("root"));' > $(FRONTEND_DIR)/src/index.tsx
	@echo 'body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; } code { font-family: source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace; }' > $(FRONTEND_DIR)/src/index.css