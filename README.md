# Junior Bank

Junior Bank is a simple banking application designed to help young people learn about managing finances.
It provides basic banking functionalities in a user-friendly interface.

## Features

- User registration and login
- Account balance viewing
- Deposit and withdrawal transactions
- Transaction history
- Daily interest calculation

## Getting Started

This project uses `make` to simplify common tasks like deployment, development, and testing.

### Prerequisites

- **Python 3.9+** and **Poetry**: For the backend.
- **Node.js** and **npm**: For the frontend. The `Makefile` will attempt to install `npm` if it's not found on Linux/macOS.
- **Git**: For cloning the repository.

### 1-Click Deployment

The easiest way to get Junior Bank up and running for production-like serving is with a single command:

```bash
make deploy
```

This command will:
1.  Install all backend and frontend dependencies.
2.  Run database migrations for the backend.
3.  Build the frontend for production.
4.  Start the backend server.
5.  Start a static server for the built frontend.

By default:
-   The backend server will run on `http://localhost:8000`.
-   The frontend will be accessible at `http://localhost:3000`.

**Customizing Ports for Deployment:**

You can customize the ports by setting the `BACKEND_PORT` and `FRONTEND_PORT` environment variables:

```bash
BACKEND_PORT=8001 FRONTEND_PORT=3001 make deploy
```

This would make the backend available at `http://localhost:8001` and the frontend at `http://localhost:3001`.

### Stopping the Application

To stop all servers started by `make deploy` or `make run`:

```bash
make stop
```

## Development Mode

If you want to run the application in development mode with features like backend auto-reload and frontend hot-reloading:

```bash
make run
```

This command will:
1.  Stop any currently running application servers.
2.  Start the backend server with auto-reload enabled (typically on port 8000).
3.  Start the frontend development server (typically on port 3000, but it might choose another if 3000 is busy).

**Customizing Ports for Development:**

Port customization with `BACKEND_PORT` also works for the development backend:

```bash
BACKEND_PORT=8001 make run
```
Note: The frontend development server started by `npm start` might have its own way of configuring the port (e.g., via `.env` file or command-line arguments not directly covered by `FRONTEND_PORT` in `make run`). `REACT_APP_API_BASE_URL` is set automatically based on `BACKEND_PORT` for the frontend dev server.

## Running Integration Tests

This project includes integration tests to verify API functionality. To run these tests:

```bash
make test-integration
```

This command will:
1.  Ensure any existing application servers are stopped.
2.  Set up the database by running migrations.
3.  Build the frontend for production (as some tests might interact with static assets or frontend-related API behavior).
4.  Start the backend and a static frontend server on default or specified ports.
5.  Run the integration tests (located in `tests/integration/`).
6.  Stop all started servers after the tests complete.

Test reports will be printed to the console.

**Customizing Ports for Integration Tests:**

You can also specify custom ports for the servers during integration testing:

```bash
BACKEND_PORT=8002 FRONTEND_PORT=3002 make test-integration
```
The tests will then target these specified ports.

## Other Useful Makefile Targets

-   `make install`: Installs backend and frontend dependencies.
-   `make build-frontend`: Builds the frontend for production without running servers.
-   `make migrate-backend`: Runs database migrations.
-   `make clean`: Stops servers and removes build artifacts and virtual environments.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
