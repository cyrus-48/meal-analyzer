#!/bin/bash

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored status messages
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Set default port if not specified
export PORT=${PORT:-10000}

print_status "🚀 Starting FoodAI build process..."

# Setup virtual environment
print_status "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Install dependencies
print_status "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || {
    print_error "Failed to install dependencies"
    exit 1
}

# Collect static files
print_status "🎨 Collecting static files..."
python manage.py collectstatic --noinput || {
    print_error "Failed to collect static files"
    exit 1
}

# Run migrations
print_status "🔄 Running database migrations..."
python manage.py migrate || {
    print_error "Failed to run migrations"
    exit 1
}

# Start Gunicorn with your current configuration
print_status "🌟 Starting Gunicorn server..."
gunicorn config.wsgi:application \
    --workers=2 \
    --threads=2 \
    --bind=0.0.0.0:$PORT \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- \
    --capture-output \
    --enable-stdio-inheritance &

# Start Celery worker with your current configuration
print_status "🌾 Starting Celery worker..."
celery -A config worker \
    --concurrency=1 \
    -B \
    -l INFO \
    --without-heartbeat \
    --without-gossip \
    --without-mingle &

# Store PIDs for cleanup
echo $! > celery.pid
echo $! > gunicorn.pid

# Trap SIGTERM and SIGINT
cleanup() {
    print_status "📥 Shutting down services..."
    kill $(cat celery.pid)
    kill $(cat gunicorn.pid)
    rm -f celery.pid gunicorn.pid
    deactivate
    print_status "✅ Cleanup completed"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Wait for all background processes
wait

print_status "✅ Build process completed!"