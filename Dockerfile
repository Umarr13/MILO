# Use an official lightweight Python image.
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/src/app

# Install system dependencies (needed for compiling ML libraries if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ backend/
COPY data_pipeline/ data_pipeline/
COPY models/ models/
COPY milo.db .

# Expose the port the app runs on
EXPOSE 8000

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
