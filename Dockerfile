# Dockerfile for Marbaras E-commerce
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create logs, static, and media directories (if not using Railway Volume)
# Railway Volume should be mounted at /app/media
RUN mkdir -p /app/logs /app/static /app/media /app/media/products /app/media/products/multiple

# Expose port
EXPOSE 8000

# Use entrypoint script
# Usefull
ENTRYPOINT ["/app/entrypoint.sh"]

