# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies (the most important step for FFmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# 5. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the project code into the container
COPY . .

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]