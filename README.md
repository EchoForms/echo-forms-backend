# Echo Forms Backend

This is the backend service for Echo Forms, built with FastAPI and PostgreSQL.

## Setup Instructions

### 1. Clone the repository

```sh
git clone git@github.com:EchoForms/echo-forms-backend.git
cd echo-forms-backend
```

### 2. Create and activate a virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

Or, if you haven't generated a requirements.txt yet:

```sh
pip install fastapi 'uvicorn[standard]' psycopg2-binary sqlalchemy
```

### 4. Start the FastAPI server locally

```sh
uvicorn main:app --reload
```

The server will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Next Steps

- Add PostgreSQL database connection
- Add API endpoints
- Add authentication

_This README will be updated as development progresses.

## PostgreSQL Setup (Mac)

1. **Install PostgreSQL:**

   ```sh
   brew install postgresql
   brew services start postgresql
   ```

2. **Create user and database:**

   ```sh
   psql postgres
   # In the psql shell:
   CREATE USER echoforms WITH PASSWORD 'password';
   CREATE DATABASE echoforms OWNER echoforms;
   \q
   ```

## FFmpeg Setup (Required for Audio Processing)

FFmpeg is required for processing audio files and extracting duration information.

### On macOS

```sh
# Using Homebrew (recommended)
brew install ffmpeg

# Or using MacPorts
sudo port install ffmpeg
```

### On Ubuntu/Debian

```sh
sudo apt install ffmpeg
```

### Verify Installation

```sh
ffmpeg -version
```

## Environment Variables

Set the following environment variable (or use the default):

```sh
DATABASE_URL=postgresql+psycopg2://echoforms:password@localhost:5432/echoforms_db
```

## Health Check

Test the server and DB connection:

- `GET /health` should return `{ "status": "ok", "db": "connected" }` if the DB is reachable.

## Database Initialization

After creating your database, run the following command to set up the tables:

```sh
psql -U echoforms -d echoforms -f schema.sql
```

This will create the initial tables (e.g., users) as defined in `schema.sql`.
