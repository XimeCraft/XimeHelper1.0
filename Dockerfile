FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir tiktoken

# Copy project files
COPY . .

# Create and set permissions for log directories
RUN mkdir -p /app/shared/logs && \
    chown -R appuser:appuser /app/shared/logs && \
    chmod 755 /app/shared/logs

# Set environment variables
ENV PYTHONPATH=/app

# Switch to app user
USER appuser

# Start command
CMD ["python", "run.py"]