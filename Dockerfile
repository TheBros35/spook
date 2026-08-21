FROM python:alpine

# Prevent .pyc files and enable unbuffered stdout/stderr for clean logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DATA_DIR=/app/data

WORKDIR /app

# System deps kept minimal - sqlite3 lib ships with the Python base image already.
# tzdata is required for the TZ env var to have any effect in Alpine.
RUN apk add --no-cache curl tzdata

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

# Directory for the persistent SQLite database (mount a volume here)
RUN mkdir -p /app/data

# Run as a non-root user
RUN adduser -D -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 4321

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:4321/ || exit 1

ENTRYPOINT ["./entrypoint.sh"]
