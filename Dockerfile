FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for building packages and running the app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
# Using the official installer script
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && mv /root/.local/bin/poetry /usr/local/bin/poetry

# Verify Poetry installation
RUN poetry --version

# Copy the pyproject.toml and poetry.lock files to the working directory
# This allows Docker to cache the dependency installation layer
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create a virtual environment inside the container
# This is common practice for Docker images to keep dependencies in the container's site-packages
RUN poetry config virtualenvs.create false

# Install all project dependencies
# This command installs dependencies defined in pyproject.toml
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Define the command to run the application
# Use uvicorn to run the FastAPI app
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
