# Dockerfile
FROM python:3.9-slim

# Add metadata labels
LABEL maintainer="Ashley Pilger <my@example.com>"
LABEL version="1.0"
LABEL description="GuardianSensor - mmWave Radar Child Safety System"
LABEL repository="https://github.com/KazeAsh/GuardianSensor"

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw/mmwave
RUN mkdir -p data/processed
RUN mkdir -p outputs/visualizations
RUN mkdir -p outputs/reports
RUN mkdir -p outputs/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]