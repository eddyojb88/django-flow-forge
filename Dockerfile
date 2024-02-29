# syntax=docker/dockerfile:1

FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get install -y g++-11 make python3 python-is-python3 pip python3.10-venv 

RUN apt-get install -y build-essential libpq-dev

# For Django:
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata 

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

# Install python venv and upgrade pip, install postgres client and requirements
RUN python -m venv /py && /py/bin/pip install --upgrade pip

RUN /py/bin/pip install -r requirements.txt

COPY . /app

WORKDIR /app
RUN mkdir -p /app/temp

RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media

RUN DEBIAN_FRONTEND=noninteractive adduser --disabled-password --no-create-home  --gecos "" app  && \
    chown -R app:app /vol && \
    chmod -R 777 /py && \
    chown -R app /app && \
    chown -R app:app /py/ && \
    chmod -R 755 /vol

CMD sleep infinity