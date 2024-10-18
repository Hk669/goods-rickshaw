# Use the official Python image as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for GeoDjango
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin python3-gdal postgresql-client

# Set the working directory
WORKDIR /logistics_platform

# Copy the requirements file and install Python dependencies
COPY requirements.txt /logistics_platform/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /logistics_platform/

RUN python manage.py runserver 0.0.0.0:8000
