# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Install PostgreSQL client library and dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    
# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code into the container
COPY . .

# Command to run your bot
CMD tail -f /dev/null

