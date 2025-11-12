#!/bin/bash
set -e

echo "=========================================="
echo "Starting Marbaras E-commerce Application"
echo "=========================================="

# Wait for database to be ready (with timeout)
echo "Waiting for database connection..."
MAX_RETRIES=30
RETRY_COUNT=0

# Use Python script to check database connection (more reliable than dbshell)
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'МагазинСребро.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    exit(0)
except Exception:
    exit(1)
EOF
    then
        echo "✅ Database connection successful!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Database is unavailable - retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Warning: Could not connect to database after $MAX_RETRIES retries"
    echo "Continuing anyway - migrations will attempt to connect..."
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "Migration failed, but continuing..."
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "Collectstatic failed, but continuing..."
}

# Create superuser if it doesn't exist (optional)
# Uncomment if you want to auto-create superuser
# python manage.py shell << EOF
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
# EOF

echo "=========================================="
echo "Starting Gunicorn..."
echo "=========================================="

# Use PORT environment variable if provided (Railway, Render, etc.), otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting Gunicorn on port $PORT..."

# Start Gunicorn
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    МагазинСребро.wsgi:application

