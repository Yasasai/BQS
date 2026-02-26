# BQS Docker Setup Guide

This application has been fully dockerized for ease of deployment and consistent environments.

## Prerequisites
- Docker and Docker Compose installed on your system.
- An `.env` file in the root directory with the following variables:
  ```env
  ORACLE_BASE_URL=your_oracle_url
  ORACLE_USER=your_oracle_user
  ORACLE_PASSWORD=your_oracle_password
  ORACLE_API_VERSION=11.12.1.0
  ```

## Services
The setup includes three inter-related services:
1.  **db**: PostgreSQL 15 database.
2.  **backend**: FastAPI application (Port 8000).
3.  **frontend**: React application served via Nginx (Port 80).

## How to Run
1.  Open a terminal in the project root.
2.  Run the following command to build and start the containers:
    ```bash
    docker-compose up --build
    ```
3.  Access the application at `http://localhost`.

## Persistent Data
- Database data is persisted in a Docker volume named `pgdata`.
- Uploaded files in the backend are currently stored in `/app/backend/uploads` inside the container. If you need these to persist across container removals, add a volume mapping for it in `docker-compose.yml`.

## Troubleshooting
- **Database Connection**: The backend automatically handles database creation and schema migrations/healing on startup. If you see connection errors, ensure the `db` service is healthy.
- **Oracle Sync**: The application attempts an initial sync on startup. Ensure your Oracle credentials in `.env` are correct.
- **Frontend API**: The frontend is configured to use a relative path `/api` which is proxied by Nginx to the backend service. This avoids CORS issues and hardcoded IP addresses.

---
*Created by Antigravity*
