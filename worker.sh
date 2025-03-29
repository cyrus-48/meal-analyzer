#!/bin/bash
source venv/bin/activate
celery -A config worker --concurrency=1 -B -l INFO