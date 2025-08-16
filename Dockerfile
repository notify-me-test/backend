# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for Pillow and other packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Use entrypoint script for database initialization and server startup
ENTRYPOINT ["./entrypoint.sh"]
