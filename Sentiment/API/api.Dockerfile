# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

ENV TRANSFORMERS_CACHE=/root/.cache
ENV HF_HOME=/root/.cache

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies with caching and verbose output
RUN pip install --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH

# Set environment variables for caching
ENV TRANSFORMERS_CACHE=/root/.cache
ENV HF_HOME=/root/.cache
ENV PYTHONUNBUFFERED=1

# Expose the port Flask will run on
EXPOSE 6000

# Run the application
CMD ["python3", "-u", "api.py"]
