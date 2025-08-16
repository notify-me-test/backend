#!/bin/bash
set -e

echo "Starting Django backend initialization..."

# Wait for database to be ready (placeholder for future external DB support)
echo "Checking database readiness..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Load sample data (only if database is empty)
echo "Loading sample data..."
python manage.py loaddata sample_data.json

# Start Django development server
echo "Starting Django server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000
