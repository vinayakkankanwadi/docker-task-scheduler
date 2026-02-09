# Use Alpine Linux with Python (lightweight)
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy the Python script
COPY app.py .

# Run the Python script
CMD ["python", "app.py"]
