# Use Python 3.12 slim image
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
    libportaudio2 \
    wget \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data/faces logs

# Download YOLO model if not present
RUN if [ ! -f yolo11n.pt ]; then \
    python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')" || \
    wget -q https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt; \
    fi

# Expose Streamlit port
EXPOSE 2524                                                                                                                                                                                                                                                                                                                                                                                                     

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:2524/_stcore/health || exit 1

# Set environment variables
ENV STREAMLIT_SERVER_PORT=2524
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Run the authentication app
CMD ["streamlit", "run", "apps/app_auth.py", "--server.port=2524", "--server.address=0.0.0.0", "--server.headless=true"]

