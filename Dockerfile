# syntax=docker/dockerfile:1

FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common g++-11 make python3 python-is-python3 pip python3.10-venv build-essential libpq-dev && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata

# Set Python to not buffer output
ENV PYTHONUNBUFFERED=1

# Copy requirements.txt to the container
COPY requirements.txt .

# Upgrade pip and install dependencies from requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/temp /vol/web/static /vol/web/media

# Create a user for running applications
RUN DEBIAN_FRONTEND=noninteractive adduser --disabled-password --no-create-home --gecos "" app && \
    chown -R app:app /vol && \
    chown -R app:app /app && \
    chmod -R 755 /vol

# Command to run on container start
CMD sleep infinity