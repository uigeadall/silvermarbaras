#!/bin/bash
set -e

echo "=========================================="
echo "Starting Marbaras E-commerce Application"
echo "=========================================="

# Wait for database to be ready (optional, useful for Docker Compose)
echo "Waiting for database..."
while ! python manage.py dbshell --command="SELECT 1" > /dev/null 2>&1; do
    echo "Database is unavailable - sleeping"
    sleep 1
done
echo "Database is up - continuing..."

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

# Start Gunicorn
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    МагазинСребро.wsgi:application

