# Sentiment Bot Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests

CMD ["python3", "-u", "bot.py"]
