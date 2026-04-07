# Quiz App Showcase Deployment Guide

This guide is for a simple project showcase deployment using one Docker Compose file.

## 1) Prepare environment

1. Install Docker Desktop (Windows) or Docker Engine with Compose.
2. Update values in `docker/.env`.
3. Set `PUBLIC_BASE_URL` to your server URL, for example `http://YOUR_PUBLIC_IP:8000`.

## 2) Provide Firebase credentials

1. Put your Firebase service account JSON at the host path configured in `docker/.env`.
2. Default configured path is `../secrets/firebase-service-account.json`.
3. Keep `FIREBASE_CREDENTIALS_PATH=/run/secrets/firebase_credentials.json`.

## 3) Start the stack

From project root:

```powershell
docker compose --env-file docker/.env -f docker/docker-compose.yml up -d --build
```

## 4) Verify services

```powershell
docker compose --env-file docker/.env -f docker/docker-compose.yml ps
```

Expected endpoints:

- Frontend: `http://YOUR_PUBLIC_IP:8501`
- Backend docs: `http://YOUR_PUBLIC_IP:8000/`

## 5) If not reachable from another machine

Open inbound firewall ports on the host and cloud security group:

- `8501` for frontend
- `8000` for backend docs/API

## 6) Useful logs

```powershell
docker compose --env-file docker/.env -f docker/docker-compose.yml logs -f backend
docker compose --env-file docker/.env -f docker/docker-compose.yml logs -f frontend
```

## 7) Stop services

```powershell
docker compose --env-file docker/.env -f docker/docker-compose.yml down
```
