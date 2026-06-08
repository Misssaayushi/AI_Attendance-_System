# Use python-slim as base
FROM python:3.11-slim

# Install system dependencies required for face_recognition (dlib) and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libx11-dev \
    libgl1 \
    libglib2.0-0 \
WORKDIR /app

# Prevent compiler out-of-memory issues by restricting dlib/cmake compilation to a single thread
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"

# Copy backend requirements first
COPY backend/Backend/requirements.txt ./backend_requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

# Install AI dependencies in the same environment
RUN pip install --no-cache-dir face_recognition opencv-python-headless

# Copy Backend app code
COPY backend/Backend/ /app/backend/

# Copy AI Module code to its expected relative path
COPY ai-module/AI_Module/ /app/ai-module/

# Set environment variables for AI paths
ENV AI_MODULE_DIR=/app/ai-module
ENV AI_DATASET_DIR=/app/ai-module/dataset
ENV PYTHONPATH=/app/backend:/app/ai-module

# Create folders for dataset, encodings, exports, and logs
RUN mkdir -p /app/ai-module/dataset /app/ai-module/encodings /app/backend/exports /app/backend/logs

EXPOSE 8000

WORKDIR /app/backend
CMD ["python", "run.py"]
