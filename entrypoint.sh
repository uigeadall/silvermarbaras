#!/bin/bash
set -e

echo "=========================================="
echo "Starting Marbaras E-commerce Application"
echo "=========================================="

# Check if DATABASE_URL is set (Railway, Render, etc.)
if [ -z "$DATABASE_URL" ] && [ -z "$MYSQL_HOST" ] && [ -z "$POSTGRES_HOST" ]; then
    echo "⚠️  Warning: No database configuration found!"
    echo "Please set DATABASE_URL or MySQL/PostgreSQL environment variables"
    echo "Continuing anyway - application may fail to start..."
else
    echo "Database configuration found, waiting for connection..."
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
except Exception as e:
    exit(1)
EOF
        then
            echo "✅ Database connection successful!"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -le 10 ]; then
            echo "Database is unavailable - retry $RETRY_COUNT/$MAX_RETRIES..."
        fi
        sleep 2
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "⚠️  Warning: Could not connect to database after $MAX_RETRIES retries"
        echo "Continuing anyway - migrations will attempt to connect..."
    fi
fi

# Ensure media directories exist (create if Railway Volume is not mounted)
echo "Ensuring media directories exist..."
mkdir -p /app/media/products /app/media/products/multiple || {
    echo "Could not create media directories, but continuing..."
}

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "Migration failed, but continuing..."
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    echo "Collectstatic failed, but continuing..."
}
# Ensure banner exists in staticfiles (always copy after collectstatic)
if [ -f "static/images/banner.jpg" ]; then
    echo "✅ Ensuring banner.jpg is in staticfiles..."
    mkdir -p staticfiles/images
    cp static/images/banner.jpg staticfiles/images/banner.jpg && echo "✅ Banner copied successfully" || echo "⚠️  Could not copy banner"
elif [ -f "staticfiles/images/banner.jpg" ]; then
    echo "✅ Banner already exists in staticfiles"
else
    echo "⚠️  Warning: Banner not found in static/images/"
fi

# Import data if database is empty (only on first run)
echo "Checking if database needs initial data import..."
python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'МагазинСребро.settings')
django.setup()
from django.db import connection
from django.core.management import call_command

try:
    # Check if database has any data
    with connection.cursor() as cursor:
        # Check if any tables exist and have data
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
        table_count = cursor.fetchone()[0]
        
        if table_count > 0:
            # Check if Product table exists and has data
            try:
                cursor.execute("SELECT COUNT(*) FROM ecommerce_product")
                product_count = cursor.fetchone()[0]
                
                if product_count == 0:
                    print("📦 Database is empty, importing initial data...")
                    try:
                        # Try to import from local file first (after deploy)
                        import os
                        local_file = '/app/data.json'
                        if os.path.exists(local_file):
                            print(f"Found local data.json, importing...")
                            call_command('import_data', '--file', local_file)
                        else:
                            # Fallback: try to download from GitHub
                            print("Local file not found, trying GitHub...")
                            call_command('import_data', '--url', 'https://raw.githubusercontent.com/uigeadall/marbaras123/newone/data.json')
                        print("✅ Data imported successfully!")
                    except Exception as e:
                        print(f"⚠️  Could not import data: {e}")
                        print("You can import data manually later using: python manage.py import_data")
                else:
                    print(f"✅ Database already has {product_count} products, skipping import.")
            except Exception as e:
                # Table doesn't exist yet, skip import
                print(f"⚠️  Could not check database: {e}")
        else:
            print("⚠️  No tables found, skipping data import.")
except Exception as e:
    print(f"⚠️  Could not check database: {e}")
EOF

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

