# Plus One DB Project

A REST API for managing users, venues, events, and RSVPS.

## Requirements

- Python 3.13+
- PostgreSQL 18

## Setup

1. Clone the repo;
2. Create and activate a venv in the root directory: `python -m venv .venv` and `source .venv/bin/activate`;
3. Install project requirements via `pip install requirements.txt`;
4. Create a .env file and copy the contents of .env.example into it. Set the database URL to your local Postgres connection string. Generate a JWT secret key and copy it into .env as JWT_SECRET;
5. Create the database 'nc_plus_one' by running the setup file: `psql -f setup.sql`;
6. Seed the database: `python db/data/seed/seed.py`;
7. Start the server: `uvicorn main:app --reload`.

The server is now running. Visit http://127.0.0.1:8000/docs for documentation.



