FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create model directory
RUN mkdir -p src/models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]