# Docker / Compose

Bring up services (builds images):

```bash
docker compose up --build
```

Services:
- `mongo` — MongoDB exposed on `27017` (data persisted to a docker volume)
- `backend` — FastAPI app on `8000` (built from `backend/Dockerfile`)
- `frontend` — Next.js app on `3000` (built from `frontend/Dockerfile`)

Notes:
- The backend attempts to connect to MongoDB using `MONGO_URL` (default: `mongodb://mongo:27017`).
- The backend image uses the Playwright Python base image so browser automation will work in-container.
