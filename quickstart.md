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

## ✅ You're All Set!

With these three steps, your environment is ready for both API development and NLP research.

### Common Commands Summary

- `make setup`: Install or update dependencies.
- `make run-api`: Run the local web server.
- `make test`: Run automated tests.
- `make format`: Format your code.
- `make lint`: Check your code for errors.
- `poetry run jupyter notebook`: Start Jupyter for research.
