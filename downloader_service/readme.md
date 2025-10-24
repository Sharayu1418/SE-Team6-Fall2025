# SmartCache AI - Downloader Service

This repository contains the **Django-based backend microservice** for the **SmartCache AI** project.  
Its primary role is to **download multimedia content** — including video, audio, and text — from provided URLs and store them securely in a **central S3 bucket**, making them accessible to other services in the SmartCache ecosystem.

---

## 🧩 Prerequisites

Before setting up the service, ensure the following are installed on your local machine:

- **Git**
- **Docker**

---

## 🚀 Getting Started

Follow these steps to get the **Downloader Service** running locally using Docker.  
> All commands should be run from the **root of the repository**, i.e., from `SE-Team6-Fall2025/`.

---

### 1. Set Up Environment Variables

The service requires AWS credentials to connect to S3. These are configured in a `.env` file that **must not be committed to Git**.

#### Create the `.env` file
```bash
cp downloader_service/.env.example downloader_service/.env
```

#### Edit the `.env` file
Open `downloader_service/.env` and fill in your **AWS credentials** and **S3 bucket details**.

---

### 2. Build the Docker Image

Build the Docker image, which packages the Django application and all dependencies (including **FFmpeg**).

```bash
docker build -t downloader-service ./downloader_service
```

---

### 3. Run Database Migrations

Before running the service, initialize the database by applying migrations.  
This step creates the required tables inside the container.

#### macOS / Linux
```bash
docker run --rm --env-file ./downloader_service/.env -v "$(pwd)/downloader_service:/app" downloader-service python manage.py migrate
```

#### Windows (Command Prompt)
```bash
docker run --rm --env-file ./downloader_service/.env -v "%cd%/downloader_service:/app" downloader-service python manage.py migrate
```

---

### 4. Start the Service

Once migrations are complete, you can start the main server.  
The service will be available locally at **http://127.0.0.1:8000**.

#### macOS / Linux
```bash
docker run --rm -p 8000:8000 --env-file ./downloader_service/.env -v "$(pwd)/downloader_service:/app" downloader-service
```

#### Windows (Command Prompt)
```bash
docker run --rm -p 8000:8000 --env-file ./downloader_service/.env -v "%cd%/downloader_service:/app" downloader-service
```

---

## 🧪 Testing the Service

To verify the service is running correctly, test the primary **download endpoint** using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/download/ \
-H "Content-Type: application/json" \
-d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "type": "VIDEO"}'
```

If successful, you will receive a **202 Accepted** response, and the service will begin downloading and uploading the file to your **S3 bucket**.

---

## 📂 Directory Overview

```
SE-Team6-Fall2025/
│
├── downloader_service/
│   ├── Dockerfile
│   ├── .env.example
│   ├── manage.py
│   ├── requirements.txt
│   └── app/                 # Django application code
│
└── README.md
```

---

## 🛠️ Tech Stack

- **Django** – Web framework for backend logic and API handling  
- **Docker** – Containerization for consistent local and cloud environments  
- **AWS S3** – Centralized object storage for downloaded content  
- **FFmpeg** – Multimedia processing for video and audio downloads  

---

## ⚠️ Notes

- Never commit your `.env` file to the repository.  
- Ensure your AWS credentials have the necessary S3 permissions.  
- Logs and temporary files are stored in the container and can be monitored via Docker.

---

