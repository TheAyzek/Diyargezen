FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies (build-essential, libpq-dev if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Copy requirement files first for layer caching
COPY requirements.txt /app/requirements.txt
COPY web/backend/requirements.txt /app/web/backend/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir -r /app/web/backend/requirements.txt

# Copy required application core and backend folders
COPY rules /app/rules
COPY creators /app/creators
COPY etl /app/etl
COPY utils /app/utils
COPY models /app/models
COPY parsers /app/parsers
COPY assets /app/assets
COPY data /app/data
COPY web/backend /app/web/backend

# Create directory for data persistency
RUN mkdir -p /app/web/backend/data /app/desktop/data

EXPOSE 8000

WORKDIR /app/web/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
