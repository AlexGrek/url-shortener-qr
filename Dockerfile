# Use slim Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Pillow (used by qrcode)
RUN apt-get update && apt-get install -y \
    libjpeg-dev zlib1g-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (only necessary packages)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
