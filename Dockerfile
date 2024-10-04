# Use the official Python 3.12 image
FROM python:3.12.6-slim

# Install system dependencies for pandas, g++, and distutils
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-distutils \  
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Create the uploads directory
RUN mkdir -p uploads

# Expose the port your app runs on
EXPOSE 5000

# Command to run your Flask app
CMD ["python3", "flaskAPI.py"]
