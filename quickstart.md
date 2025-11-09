# ⚡ Quick Start Guide

Welcome to the Smart Expense NLP project! This guide provides the essential steps to get your development environment up and running quickly.

For more detailed information, please refer to the main [README.md](./README.md).

---

##  Prerequisites

1.  **Python 3.9+**: Make sure you have a compatible Python version installed.
2.  **Poetry**: This project uses Poetry for dependency management. Follow the [official installation guide](https://python-poetry.org/docs/#installation) to set it up.
3.  **Make**: A tool for automating command execution. It's typically pre-installed on Linux and macOS. For Windows, you can use it via WSL or install it with a package manager like Chocolatey.

---

## 🚀 Three Steps to Get Started

### Step 1: Setup the Project

This single command will create a dedicated virtual environment and install all necessary dependencies (for the API, research, and training).

```bash
# First, clone the repository from GitHub
git clone https://github.com/YOUR_USERNAME/smart-expense-nlp.git

# Navigate into the project directory
cd smart-expense-nlp

# Run the setup command from the Makefile
make setup
```

### Step 2: Run the API Server

This command starts the FastAPI development server. It includes a placeholder for the NLP model, so you can test the API endpoints immediately.

```bash
# Start the server
make run-api
```

Your API is now running. You can access it at:
- **API URL**: `http://127.0.0.1:8000`
- **Interactive Docs**: `http://127.0.0.1:8000/docs` (Recommended for testing)

### Step 3: Launch Jupyter for Research

This command starts a Jupyter Notebook server within the project's virtual environment, giving you access to all the installed data science and ML libraries for experimentation.

```bash
# Launch Jupyter
poetry run jupyter notebook
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


**Last Updated:** 2024-11-09  
**Version:** 1.0.0