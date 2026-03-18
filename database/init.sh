#!/bin/bash
# Initialize database — run once
set -e

DB_NAME=${DB_NAME:-retail_db}
DB_USER=${DB_USER:-postgres}
DB_PASS=${DB_PASS:-REDACTED_SEE_ENV_EXAMPLE}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo "Creating database $DB_NAME..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"

echo "Running migrations..."
for f in $(ls migrations/*.sql | sort); do
    echo "  Applying $f..."
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $f
done

echo "Seeding data..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f seed.sql

echo "Done."
