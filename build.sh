#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "===> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "===> Collecting static files for WhiteNoise..."
python manage.py collectstatic --no-input

echo "===> Applying database migrations..."
python manage.py migrate

echo "===> Seeding hospital departments, doctors, and demo accounts..."
python manage.py seed_data

echo "===> Build completed successfully! Application is ready to launch."
