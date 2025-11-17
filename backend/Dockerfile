# Backend Dockerfile - FastAPI
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    wget \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ../ .

# Create necessary directories
RUN mkdir -p data/faces logs

# Download YOLO model if not present
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')" || \
    wget -q https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt

# Expose FastAPI port
EXPOSE 8021

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8021/api/health || exit 1

# Run FastAPI with uvicorn
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8021", "--workers", "1"]
