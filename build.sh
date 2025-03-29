#!/bin/bash

echo "🚀 Starting FoodAI build process..."

# Create and activate virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Start Gunicorn
echo "🌟 Starting Gunicorn server..."
gunicorn config.wsgi:application --workers=2 --threads=2 --bind 0.0.0.0:$PORT &

# Start Celery worker
echo "🌾 Starting Celery worker..."
celery -A config worker --concurrency=1 -B -l INFO &

# Wait for all processes
wait

echo "✅ Build process completed!"