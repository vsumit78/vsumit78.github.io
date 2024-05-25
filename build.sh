#!/usr/bin/env bash

# Install build tools and system dependencies
apt-get update && apt-get install -y build-essential python3-dev tzdata

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate
