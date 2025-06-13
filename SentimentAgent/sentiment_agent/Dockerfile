# Enhanced Dockerfile for Sentiment Analysis Agent

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY sentiment_agent ./sentiment_agent
COPY ui/app.py ./app.py
COPY config ./config
COPY ci ./ci

# Add healthcheck script (optional)
COPY scripts/healthcheck.sh ./scripts/healthcheck.sh
RUN chmod +x ./scripts/healthcheck.sh

# Expose Streamlit default port
EXPOSE 8501

# Entrypoint
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]

# HEALTHCHECK
HEALTHCHECK CMD ["bash", "./scripts/healthcheck.sh"]
