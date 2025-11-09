# 🧠 Smart Expense NLP API

> Intelligent Indonesian Expense Parser using IndoBERT + Hybrid NLP Approach

API untuk parsing expense text informal Indonesia menggunakan kombinasi **IndoBERT NER** dan **Rule-based Regex** untuk ekstraksi otomatis item name, price, quantity, dan currency.

[![CI Pipeline](https://github.com/erwDev/smart-expense-nlp/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/smart-expense-nlp/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

---

## Dokumentasi Lain
- [Quickstart Guide](./quickstart.md)
- [Development Requirements](./requirements-dev.txt)

## 📋 Table of Contents

- [Background](#background)
- [Features](#features)
- [Quick Start](#quick-start)
- [Research Workflow](#research-workflow)
- [Production Workflow](#production-workflow)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Team](#team)

---

## 🎯 Background

Personal finance management di Indonesia menghadapi tantangan:

- ❌ **Manual entry ribet** - isi 4-5 field per transaksi
- ❌ **NLP tools ga ngerti Indonesian slang** - "10k", "15rb", "nasi goreng"
- ❌ **Privacy concerns** - upload data finansial ke cloud
- ❌ **Low adoption** - complexity leads to abandonment

### 💡 Solution: Hybrid NLP System

Kombinasi **Rule-based (Regex)** + **Deep Learning (IndoBERT NER)**:

```
Input:  "2x nasi goreng @15rb"
Output: {
  "items": ["nasi goreng"],
  "quantity": 2,
  "unit_price": 15000,
  "total_price": 30000,
  "currency": "IDR"
}
```

---

## ✨ Features

### 🔬 Research Features
- ✅ IndoBERT-based Named Entity Recognition (NER)
- ✅ BIO tagging for token classification
- ✅ Custom Indonesian expense dataset (2000+ samples)
- ✅ Training on Google Colab (FREE GPU T4)
- ✅ Experiment tracking with Wandb
- ✅ Model evaluation metrics (F1-score, precision, recall)

### 🚀 Production Features
- ✅ FastAPI REST API
- ✅ Hybrid extraction (NER + Regex)
- ✅ Offline-first (no cloud dependency)
- ✅ <200ms inference latency
- ✅ Docker containerization
- ✅ Railway deployment ready

### 🇮🇩 Language Support
- ✅ Indonesian slang: "nasi goreng", "es teh manis"
- ✅ Number formats: `10k`, `15rb`, `20ribu`, `25.000`
- ✅ Complex patterns: `2x bakso @12rb`, `nasi + ayam 15000`
- ✅ Typos tolerance: "mie aym", "nasi goren"

---

## ⚡ Quick Start

### For Users (Testing API)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
cd smart-expense-nlp

# 2. Run with Docker (RECOMMENDED)
docker-compose up

# 3. Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "nasi goreng 15rb"}'

# 4. Open Interactive Docs
# http://localhost:8000/docs
```

### For Researchers (Training Model)

```bash
# Option 1: Google Colab (RECOMMENDED - FREE GPU!)
# 1. Open: notebooks/train_on_colab.ipynb
# 2. Upload to Google Colab
# 3. Runtime → Change runtime type → T4 GPU
# 4. Run all cells

# Option 2: Local Training (if you have GPU)
setup-training.bat  # Windows
./setup-training.sh  # Linux/Mac
jupyter notebook notebooks/03_train_model_local.ipynb
```

---

## 🔬 Research Workflow

### Phase 1: Data Collection & Labeling (Week 1-2)

**Goal:** Create 2000+ labeled Indonesian expense samples

```bash
# 1. Setup local environment
setup-local.bat  # Windows
./setup-local.sh  # Linux/Mac

# 2. Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Start data exploration
jupyter notebook notebooks/01_data_exploration.ipynb
```

**Critical Points:**
- [ ] **Data Quality** - BIO tagging consistency
- [ ] **Coverage** - 10+ expense categories (food, transport, shopping)
- [ ] **Variation** - Multiple number formats (10k, 15rb, 20ribu)
- [ ] **Validation** - Inter-annotator agreement >80%

**Files:**
- `data/raw/labelling_template.csv` - Template untuk labeling
- `data/raw/README.md` - Labeling guidelines
- `scripts/validate_labels.py` - Validasi consistency

---

### Phase 2: Training on Google Colab (Week 3-4)

**Goal:** Train IndoBERT NER model dengan F1-score ≥85%

#### Step-by-Step Guide:

**1. Clone Repo ke Colab**

```python
# Cell 1: Clone repository
!git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
%cd smart-expense-nlp

# Cell 2: Install dependencies
!pip install -q -r requirements-training.txt

# Cell 3: Mount Google Drive (optional - untuk save model)
from google.colab import drive
drive.mount('/content/drive')
```

**2. Setup Wandb (Experiment Tracking)**

```python
# Cell 4: Login Wandb
import wandb
wandb.login()  # Masukkan API key dari https://wandb.ai/authorize
```

**3. Load & Preprocess Data**

```python
# Cell 5: Load dataset
import pandas as pd

df = pd.read_csv('data/raw/labeled_expenses.csv')
print(f"Dataset size: {len(df)} samples")
print(f"Unique labels: {df['labels'].str.split().explode().unique()}")

df.head()
```

**4. Train Model**

```python
# Cell 6: Load config
import yaml

with open('configs/training_config.yaml') as f:
    config = yaml.safe_load(f)

# Cell 7: Initialize model
from transformers import AutoModelForTokenClassification, AutoTokenizer

model = AutoModelForTokenClassification.from_pretrained(
    config['model']['name'],
    num_labels=config['model']['num_labels']
)
tokenizer = AutoTokenizer.from_pretrained(config['model']['name'])

# Cell 8: Training
from transformers import Trainer, TrainingArguments

# ... (see notebooks/train_on_colab.ipynb for full code)

trainer.train()
```

**5. Evaluate & Export**

```python
# Cell 9: Evaluate on test set
results = trainer.evaluate(test_dataset)
print(f"F1-Score: {results['eval_f1']:.4f}")
print(f"Precision: {results['eval_precision']:.4f}")
print(f"Recall: {results['eval_recall']:.4f}")

# Cell 10: Save model
model.save_pretrained("./models_exported/indobert-expense-ner")
tokenizer.save_pretrained("./models_exported/indobert-expense-ner")

# Cell 11: Download to Google Drive
!cp -r ./models_exported/indobert-expense-ner /content/drive/MyDrive/
```

**Critical Points:**
- [ ] **Training Stability** - Loss converges, no NaN
- [ ] **Overfitting Check** - Train/Val loss gap <10%
- [ ] **F1-Score Target** - ≥85% on test set
- [ ] **Inference Speed** - <200ms per query
- [ ] **Model Size** - <500MB for deployment

**Commands:**
```bash
# Monitor training
# Wandb: https://wandb.ai/YOUR_USERNAME/smart-expense-nlp

# Download trained model
# From Colab: files.download('models_exported.zip')
# From Drive: Download folder
```

---

### Phase 3: Model Evaluation (Week 4)

**Goal:** Validate model performance & error analysis

```bash
# 1. Run evaluation notebook
jupyter notebook notebooks/04_evaluation.ipynb

# 2. Generate metrics report
python scripts/evaluate.py \
  --model models_exported/indobert-expense-ner \
  --test data/splits/test.csv \
  --output evaluation_report.json
```

**Critical Points:**
- [ ] **Entity-level F1** - Per entity type (ITEM, PRICE)
- [ ] **Exact Match** - Both item + price correct ≥80%
- [ ] **Error Patterns** - Analyze common failures
- [ ] **Confusion Matrix** - Identify misclassifications
- [ ] **Confidence Calibration** - Validate confidence scores

**Metrics to Check:**
```json
{
  "overall_f1": 0.87,
  "item_f1": 0.89,
  "price_f1": 0.94,
  "exact_match": 0.82,
  "inference_time_ms": 150
}
```

---

## 🚀 Production Workflow

### Phase 4: FastAPI Integration (Week 5)

**Goal:** Build production-ready API endpoint

```bash
# 1. Test inference locally
venv\Scripts\activate
python scripts/test_inference.py \
  --model models_exported/indobert-expense-ner \
  --text "nasi goreng 15rb"

# 2. Run FastAPI dev server
uvicorn src.api.main:app --reload

# 3. Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "2x bakso @12rb"}'

# 4. Open Swagger UI
# http://localhost:8000/docs
```

**Critical Points:**
- [ ] **API Response Time** - <200ms P95 latency
- [ ] **Error Handling** - Proper 4xx/5xx responses
- [ ] **Input Validation** - Pydantic schemas
- [ ] **Confidence Scores** - Return prediction confidence
- [ ] **Logging** - Request/response tracking

---

### Phase 5: Docker Testing (Week 5)

**Goal:** Test containerized deployment

```bash
# 1. Build Docker image
docker-compose build

# 2. Run container
docker-compose up -d

# 3. Check health
curl http://localhost:8000/health

# 4. Test inference
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "es teh manis 10k"}'

# 5. View logs
docker-compose logs -f api

# 6. Stop container
docker-compose down
```

**Critical Points:**
- [ ] **Image Size** - <2GB (compressed)
- [ ] **Startup Time** - <10s
- [ ] **Memory Usage** - <512MB idle
- [ ] **CPU Usage** - <50% during inference
- [ ] **Health Check** - Passes consistently

---

### Phase 6: Railway Deployment (Week 6)

**Goal:** Deploy to production

```bash
# 1. Push to GitHub
git add .
git commit -m "feat: production ready v1.0"
git push origin main

# 2. Connect Railway
# - Login: https://railway.app
# - New Project → Deploy from GitHub
# - Select repo: smart-expense-nlp
# - Railway auto-detects Dockerfile

# 3. Configure environment variables
# Railway Dashboard → Variables:
ENV=production
API_HOST=0.0.0.0
API_PORT=8000

# 4. Deploy
# Railway auto-deploys on push to main

# 5. Get public URL
# Railway Dashboard → Settings → Domains
# https://smart-expense-nlp.up.railway.app
```

**Critical Points:**
- [ ] **Deployment Success** - No build errors
- [ ] **Public Access** - URL accessible
- [ ] **Health Check** - `/health` returns 200
- [ ] **HTTPS** - SSL certificate active
- [ ] **Monitoring** - Uptime tracking setup

---

## 📁 Project Structure

```
smart-expense-nlp/
├── .github/workflows/       # CI/CD pipelines
│   └── ci.yml              # Test, lint, docker build
│
├── configs/                 # Configuration files
│   ├── training_config.yaml
│   └── inference_config.yaml
│
├── data/                    # Datasets
│   ├── raw/                # Labeled samples
│   │   ├── labeled_expenses.csv
│   │   ├── labelling_template.csv
│   │   └── README.md
│   ├── processed/          # Preprocessed data
│   └── splits/             # Train/val/test splits
│
├── docs/                    # Documentation
│   ├── TRAINING_GUIDE.md
│   └── DEPLOYMENT_GUIDE.md
│
├── models_exported/         # Trained models
│   └── indobert-expense-ner/
│       ├── pytorch_model.bin
│       ├── config.json
│       └── tokenizer.json
│
├── notebooks/               # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_train_model_local.ipynb
│   ├── 04_evaluation.ipynb
│   └── train_on_colab.ipynb  # ⭐ Main training script
│
├── scripts/                 # Utility scripts
│   ├── preprocess_data.py
│   ├── train.py
│   ├── evaluate.py
│   └── test_inference.py
│
├── src/                     # Source code
│   ├── api/                # FastAPI application
│   │   ├── main.py
│   │   └── routes/
│   │       └── parse.py
│   ├── models/             # Model inference
│   │   └── inference.py
│   ├── data/               # Data processing
│   └── regex/              # Regex patterns
│
├── tests/                   # Unit tests
│   └── test_api.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Production image
├── requirements.txt         # Production deps
├── requirements-dev.txt     # Development deps
├── requirements-training.txt # Training deps
├── setup-local.bat         # Windows setup
├── setup-local.sh          # Linux/Mac setup
├── quickstart.md           # Quick reference
└── README.md               # This file
```

---

## 📚 API Documentation

### Endpoints

#### `GET /`
Welcome message

**Response:**
```json
{
  "message": "Welcome to Smart Expense NLP API"
}
```

#### `GET /health`
Health check with system metrics

**Response:**
```json
{
  "status": "ok",
  "message": "API is running",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "system": "Linux",
  "python_version": "3.10.12",
  "cpu_usage_percent": 15.2,
  "memory_usage_percent": 45.8
}
```

#### `POST /parse`
Parse Indonesian expense text

**Request Body:**
```json
{
  "text": "2x nasi goreng @15rb"
}
```

**Response:**
```json
{
  "items": ["nasi goreng"],
  "quantity": 2,
  "unit_price": 15000,
  "total_price": 30000,
  "currency": "IDR",
  "confidence": 0.92,
  "method": "hybrid",
  "raw_text": "2x nasi goreng @15rb"
}
```

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🛠️ Development

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git
cd smart-expense-nlp

# 2. Setup environment
# Windows:
setup-local.bat

# Linux/Mac:
chmod +x setup-local.sh
./setup-local.sh

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 4. Verify installation
python -c "import fastapi, torch, transformers; print('✅ All OK!')"
```

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/
```

---

## 🚢 Deployment

### Environment Variables

Create `.env` file:

```env
# Environment
ENV=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Configuration
MODEL_PATH=models_exported/indobert-expense-ner

# Logging
LOG_LEVEL=INFO

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn
WANDB_API_KEY=your-wandb-key
```

### Railway Deployment

1. **Push to GitHub:**
```bash
git push origin main
```

2. **Connect Railway:**
   - Login: https://railway.app
   - New Project → Deploy from GitHub
   - Select: `smart-expense-nlp`

3. **Configure:**
   - Set environment variables
   - Railway auto-detects `Dockerfile`
   - Deploy automatically on push

4. **Monitor:**
   - Logs: Railway Dashboard
   - Metrics: `/health` endpoint

---

## 👥 Team

**Team Members:**
- Rahmanda Putri Setiawati (22/492129/PA/21069)
- Dian Kartika Putri (23/512622/PA/21892)
- Erlin Meutia Febriani (23/514273/PA/21981)
- Benedictus Erwin Widianto (23/520176/PA/22350)
- Satya Wira Pramudita (24/543649/PA/23102)
- Widad Muhammad Rafi (24/545635/PA/23190)

**Project:** Text Processing & Sentiment Classification (TPSC)  
**Institution:** Universitas Gadjah Mada  
**Year:** 2024/2025

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **IndoBERT:** [indobenchmark/indobert-base-p1](https://huggingface.co/indobenchmark/indobert-base-p1)
- **Hugging Face:** Transformers library
- **Google Colab:** Free GPU for training
- **Railway:** Easy deployment platform

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/smart-expense-nlp/issues)
- **Documentation:** [docs/](./docs/)
- **Email:** your-email@ugm.ac.id

---

**Made with ❤️ by Smart Expense NLP Team**