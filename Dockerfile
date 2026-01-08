FROM python:3.11-slim

# Set working directory INSIDE container
WORKDIR /app

# System deps (optional but recommended)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ONLY the app directory into /app
COPY app/ .

EXPOSE 8080

# IMPORTANT: app.py is now at /app/app.py
CMD ["streamlit", "run", "app.py", \
    "--server.port=8080", \
    "--server.address=0.0.0.0"]
