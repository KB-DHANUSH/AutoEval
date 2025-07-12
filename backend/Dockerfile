# Use the official Python slim image as a base
FROM python:3.13-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    file \
    unzip \
    wget \
    poppler-utils \
    tesseract-ocr \
    pandoc \
    libxml2-dev \
    libxslt1-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it for security
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the port your application runs on
EXPOSE 5000

# Define the default command to run your application
CMD ["python", "app.py"]
