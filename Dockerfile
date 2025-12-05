FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (untuk caching)
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    transformers==4.35.0 \
    torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    psutil==5.9.6 \
    python-dotenv==1.0.0 \
    gdown==4.7.1 \
    requests==2.31.0

# Copy application code
COPY . .

# Create directories for model
RUN mkdir -p models_exported/indobert-expense-ner-model/models_exported

# Expose port
EXPOSE 8000

# Health check (tunggu 2 menit untuk download model)
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]