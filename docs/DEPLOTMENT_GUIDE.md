# Deployment Guide

## Phase 1: Local Testing

### 1. Test Inference Locally
```bash
venv\Scripts\activate
uvicorn src.api.main:app --reload
```

### 2. Test Endpoints
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/parse -d '{"text":"nasi goreng 15rb"}'
```

---

## Phase 2: Docker Testing

### 1. Build Image
```bash
docker-compose build
```

### 2. Run Container
```bash
docker-compose up
```

### 3. Test Container
```bash
curl http://localhost:8000/health
```

---

## Phase 3: Deploy to Railway

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for production"
git push origin main
```

### 2. Connect Railway
1. Login to https://railway.app
2. New Project → Deploy from GitHub
3. Select repository: `smart-expense-nlp`
4. Railway auto-detects Dockerfile

### 3. Configure Environment
```env
ENV=production
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Deploy
- Railway automatically builds & deploys
- Get public URL: `https://your-app.up.railway.app`

---

## Monitoring

### Health Check
```bash
curl https://your-app.up.railway.app/health
```

### Logs
```bash
# Railway Dashboard → Deployments → Logs
```