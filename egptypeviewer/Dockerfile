# TypeGraph Explorer - Dash Application Container
# Base image: Python 3.12 slim

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY egptypeviewer/ ./egptypeviewer/
COPY assets/ ./assets/

# Expose the Dash default port
EXPOSE 8050

# Set working directory to the package containing app.py
WORKDIR /app/egptypeviewer

# Get the data"$DIR/$f"
RUN curl -z types_def.json -L -o types_def.json https://github.com/Shapedsundew9/erasmus-gp/releases/download/latest-data/types_def.json

# Run the application
CMD ["python", "app.py"]
