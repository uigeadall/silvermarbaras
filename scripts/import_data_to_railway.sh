#!/bin/bash
# Script to import data.json into Railway MySQL database

echo "📦 Importing data to Railway MySQL..."

# Download data.json from GitHub
echo "Downloading data.json from GitHub..."
curl -o /tmp/data.json https://raw.githubusercontent.com/uigeadall/marbaras123/newone/data.json

# Check if file was downloaded
if [ ! -f /tmp/data.json ]; then
    echo "❌ Failed to download data.json"
    exit 1
fi

echo "✅ Downloaded data.json ($(wc -c < /tmp/data.json) bytes)"

# Use Railway CLI to run Django management command
echo "Importing data using Django loaddata..."
railway run python manage.py loaddata /tmp/data.json

# Clean up
rm -f /tmp/data.json

echo "✅ Done!"

