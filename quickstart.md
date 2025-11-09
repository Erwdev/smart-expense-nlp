# ⚡ Quick Start Guide

Complete reference untuk setup project dari 0 sampai production!

---

## 🎯 Choose Your Path

### 👨‍🔬 **Path A: Researcher** (Training Model)
➡️ Jump to [Research Workflow](#research-workflow)

### 👨‍💻 **Path B: Developer** (Testing API)
➡️ Jump to [Production Workflow](#production-workflow)

### 🚀 **Path C: DevOps** (Deployment)
➡️ Jump to [Deployment Workflow](#deployment-workflow)

---

## 🔬 Research Workflow

### Goal: Train IndoBERT NER Model

#### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
cd smart-expense-nlp
```

#### Step 2: Setup Local Environment (Optional - untuk data labeling)

```bash
# Windows
setup-local.bat

# Linux/Mac
chmod +x setup-local.sh
./setup-local.sh

# Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

#### Step 3: Label Dataset

```bash
# Open Jupyter
jupyter notebook notebooks/01_data_exploration.ipynb

# File template: data/raw/labelling_template.csv
# Target: 2000+ labeled samples
```

#### Step 4: Train on Google Colab (RECOMMENDED!)

**Why Colab?**
- ✅ FREE GPU (Tesla T4)
- ✅ No local GPU needed
- ✅ Faster training (~30-60 min)
- ✅ Pre-installed ML libraries

**Steps:**

**4.1. Upload Notebook to Colab**

```
1. Open Google Drive
2. Create folder: smart-expense-nlp
3. Upload: notebooks/train_on_colab.ipynb
4. Right-click → Open with → Google Colaboratory
```

**4.2. Setup Colab Environment**

```python
# Cell 1: Check GPU
!nvidia-smi

# Cell 2: Clone repository
!git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
%cd smart-expense-nlp

# Cell 3: Install dependencies
!pip install -q -r requirements-training.txt

# Cell 4: Verify installation
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

**4.3. Mount Google Drive (untuk save model)**

```python
# Cell 5: Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Upload dataset dari local ke Drive
# Drive/MyDrive/smart-expense-nlp/data/raw/labeled_expenses.csv
```

**4.4. Train Model**

```python
# Cell 6: Load dataset
import pandas as pd
df = pd.read_csv('/content/drive/MyDrive/smart-expense-nlp/data/raw/labeled_expenses.csv')
print(f"Dataset size: {len(df)}")

# Cell 7-10: Run training cells
# (See full notebook for complete code)

# Training will take ~30-60 minutes
```

**4.5. Download Trained Model**

```python
# Option A: Download directly
from google.colab import files
!zip -r models_exported.zip models_exported/indobert-expense-ner
files.download('models_exported.zip')

# Option B: Save to Google Drive
!cp -r models_exported/indobert-expense-ner /content/drive/MyDrive/smart-expense-nlp/models_exported/
```

#### Step 5: Evaluate Model

```bash
# Back to local machine
# Extract models_exported.zip to project folder

# Run evaluation
jupyter notebook notebooks/04_evaluation.ipynb

# Expected metrics:
# - F1-Score: ≥0.85
# - Precision: ≥0.83
# - Recall: ≥0.87
# - Inference time: <200ms
```

---

## 💻 Production Workflow

### Goal: Test FastAPI Endpoint

#### Step 1: Clone & Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
cd smart-expense-nlp

# Setup (pilih salah satu)
# Option A: Docker (RECOMMENDED)
docker-compose up

# Option B: Local Python
setup-local.bat  # Windows
./setup-local.sh  # Linux/Mac
venv\Scripts\activate
uvicorn src.api.main:app --reload
```

#### Step 2: Test Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "API is running",
  "version": "1.0.0",
  "uptime_seconds": 10.5,
  "system": "Windows",
  "python_version": "3.10.11",
  "cpu_usage_percent": 12.3,
  "memory_usage_percent": 42.1
}
```

**Parse Expense:**
```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "nasi goreng 15rb"}'
```

**Expected Response:**
```json
{
  "items": ["nasi goreng"],
  "quantity": 1,
  "unit_price": 15000,
  "total_price": 15000,
  "currency": "IDR",
  "confidence": 0.89,
  "method": "hybrid",
  "raw_text": "nasi goreng 15rb"
}
```

#### Step 3: Interactive Testing

```bash
# Open Swagger UI
# Browser: http://localhost:8000/docs

# Test cases to try:
1. "bakso urat 12000"
2. "2x es teh @5rb"
3. "nasi + ayam goreng 25ribu"
4. "grab ke kampus 27.500"
5. "kopi susu 10k"
```

#### Step 4: Performance Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils
# Mac: brew install ab

# Load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -p payload.json -T application/json \
  http://localhost:8000/parse

# payload.json:
# {"text": "nasi goreng 15rb"}

# Expected results:
# - Requests per second: >100
# - Mean response time: <200ms
# - Failed requests: 0
```

---

## 🚀 Deployment Workflow

### Goal: Deploy to Railway

#### Step 1: Prepare for Production

```bash
# 1. Ensure trained model exists
ls models_exported/indobert-expense-ner/
# Should see: pytorch_model.bin, config.json, tokenizer.json

# 2. Test Docker build locally
docker-compose build
docker-compose up

# 3. Verify health
curl http://localhost:8000/health

# 4. Stop container
docker-compose down
```

#### Step 2: Push to GitHub

```bash
# 1. Add all changes
git add .

# 2. Commit with semantic message
git commit -m "feat: production ready with trained model v1.0"

# 3. Push to main branch
git push origin main

# 4. Verify on GitHub
# Check: models_exported/ folder uploaded (Git LFS if >100MB)
```

#### Step 3: Deploy to Railway

**3.1. Connect Railway**
```
1. Visit: https://railway.app
2. Sign in with GitHub
3. New Project → Deploy from GitHub repo
4. Select: smart-expense-nlp
5. Railway auto-detects Dockerfile ✅
```

**3.2. Configure Environment**
```
Railway Dashboard → Variables:
- ENV=production
- API_HOST=0.0.0.0
- API_PORT=8000
- LOG_LEVEL=INFO
```

**3.3. Deploy**
```
1. Railway auto-builds from Dockerfile
2. Wait ~5-10 minutes for build
3. Check logs: Deployments → Logs
4. Get public URL: Settings → Domains
```

**3.4. Generate Domain**
```
Settings → Networking → Generate Domain
URL: https://smart-expense-nlp-production.up.railway.app
```

#### Step 4: Verify Production

```bash
# Test public API
curl https://your-app.up.railway.app/health

curl -X POST https://your-app.up.railway.app/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "bakso 12rb"}'

# Check docs
# https://your-app.up.railway.app/docs
```

---

## 🔧 Troubleshooting

### Problem: "Module not found" in Colab

**Solution:**
```python
# Reinstall dependencies
!pip install --upgrade -r requirements-training.txt

# Restart runtime
# Runtime → Restart runtime
```

### Problem: Port 8000 already in use

**Solution:**
```bash
# Windows: Kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac: Kill process
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Problem: Docker build failed

**Solution:**
```bash
# Clear cache
docker system prune -a
docker volume prune

# Rebuild
docker-compose build --no-cache
```

### Problem: Model file too large for Git

**Solution:**
```bash
# Use Git LFS
git lfs install
git lfs track "models_exported/**/*.bin"
git add .gitattributes
git commit -m "chore: track model files with LFS"
```

---

## 📊 Critical Checkpoints

### ✅ Research Phase
- [ ] Dataset labeled (2000+ samples)
- [ ] BIO tagging consistent
- [ ] Train/val/test split done (70/15/15)
- [ ] Model F1-score ≥0.85
- [ ] Inference time <200ms
- [ ] Model exported successfully

### ✅ Development Phase
- [ ] FastAPI endpoint works
- [ ] Health check passes
- [ ] Parse endpoint returns correct JSON
- [ ] Docker container runs
- [ ] Unit tests pass
- [ ] No import errors

### ✅ Production Phase
- [ ] Docker build successful
- [ ] GitHub push complete
- [ ] Railway deployment green
- [ ] Public URL accessible
- [ ] HTTPS works
- [ ] API docs available

---

## 📚 Additional Resources

- **Full README:** [README.md](README.md)
- **Training Guide:** [docs/TRAINING_GUIDE.md](docs/TRAINING_GUIDE.md)
- **Deployment Guide:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **API Documentation:** http://localhost:8000/docs

---

## 🆘 Need Help?

1. **Check logs:**
   ```bash
   # Docker logs
   docker-compose logs -f
   
   # Railway logs
   # Dashboard → Deployments → Logs
   ```

2. **GitHub Issues:**
   https://github.com/YOUR_USERNAME/smart-expense-nlp/issues

3. **Team Contact:**
   - Email: your-email@ugm.ac.id
   - Slack: #smart-expense-nlp

---

**Last Updated:** 2024-11-09  
**Version:** 1.0.0