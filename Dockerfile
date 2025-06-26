ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
#Use official Python base image
FROM python:3.11-slim

# ENV Settings
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir \
    Flask \
    Flask-SQLAlchemy \
    Flask-Migrate \
    Flask-Login \
    Flask-WTF \
    Flask-Mail \
    Flask-Cors \
    psycopg2-binary \
    requests
RUN pip install --no-cache-dir \
    Flask-RESTful \
    Flask-RESTPlus \
    Flask-RESTX \
    Flask-SocketIO \
    Flask-Admin \
    Flask-Babel \
    Flask-Cache \
    Flask-Compress \
    Flask-Limiter \
    Flask-Security \
    Flask-Uploads \
    Flask-WhooshAlchemy

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the application and dependency files
COPY . .
RUN pip install -r requirements.txt

# Expose the default Flask port
EXPOSE 5000
# Start the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]