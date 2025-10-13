#!/bin/bash
set -e

echo "Waiting for database..."
while ! pg_isready -h db -U postgres; do
  sleep 1
done

echo "Database is ready!"

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
