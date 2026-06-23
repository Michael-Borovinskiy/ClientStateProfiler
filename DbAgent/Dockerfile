FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and web app
COPY src/ ./src/
COPY web/ ./web/
COPY manage.py .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the web server port
EXPOSE 8080

# Run gunicorn web server
CMD ["gunicorn", "web.wsgi:application", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
