# TypeGraph Explorer - Dash Application Container
# Base image: Python 3.12 slim

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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

# Run the application
CMD ["python", "app.py"]
