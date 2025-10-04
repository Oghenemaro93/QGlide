# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Cache busting - Force fresh build
ARG CACHE_BUST=2025-10-04-16:00
ENV PORT=8080
ENV ENVIRONMENT=production
ENV PIP_ONLY_BINARY=:all:
ENV GRPC_DNS_RESOLVER=native
ENV GRPC_ENABLE_FORK_SUPPORT=1
ENV GRPC_POLL_STRATEGY=epoll1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip config set global.index-url https://pypi.org/simple
RUN pip config set global.trusted-host pypi.org
RUN pip config set global.trusted-host files.pythonhosted.org
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy Firebase service account key (if exists)
# Note: In production, this should be handled via environment variables or secrets
COPY firebase-service-account.json* /app/

# Collect static files will be done at runtime

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE $PORT

# Run the application
CMD python manage.py collectstatic --noinput && exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 config.wsgi:application
