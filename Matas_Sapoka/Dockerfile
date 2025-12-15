# Use official Python image with system dependencies
FROM python:3.11-slim

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 8000

# Start the FastAPI app - using Python to read PORT env variable
CMD ["python", "-c", "import os, uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.getenv('PORT', '8000')))"]