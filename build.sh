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

print_status "✅ Build process completed successfully!"
exit 0