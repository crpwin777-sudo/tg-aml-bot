# Use lightweight official Python image
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies (if any) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app sources
COPY . .

# Don't store secrets in image; they come from env vars at runtime
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot_main.py"]

