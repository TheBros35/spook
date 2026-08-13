#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Optionally create a Django admin superuser from environment variables.
# Set DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD
# to have one created automatically on first boot (idempotent - skipped if it already exists).
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring Django superuser '$DJANGO_SUPERUSER_USERNAME' exists..."
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
fi

echo "Starting server..."
exec gunicorn spook.wsgi:application \
  --bind 0.0.0.0:4321 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --access-logfile - \
  --error-logfile -
