# Use a minimal Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the API source code
COPY api.py .

COPY requirements.txt .

# Install Flask
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port Flask will run on
EXPOSE 5000

CMD ["python3", "-u", "api.py"]
