# Training Guide

## Prerequisites
- Google Account (for Colab)
- GitHub Account
- Basic Python knowledge

## Option 1: Google Colab (Recommended - FREE GPU!)

### Step 1: Prepare Data
1. Label dataset di `data/raw/labeled_expenses.csv`
2. Upload ke Google Drive: `MyDrive/smart-expense-nlp/data/raw/`

### Step 2: Setup Colab
```python
# Upload notebook ke Colab
# notebooks/train_on_colab.ipynb
```

### Step 3: Run Training
1. Runtime → Change runtime type → T4 GPU
2. Run all cells
3. Wait ~30-60 minutes

### Step 4: Download Model
Model tersimpan di: `models_exported/indobert-expense-ner/`

---

## Option 2: Local Training (Jika punya GPU)

### Requirements:
- NVIDIA GPU with CUDA support
- 16GB+ RAM
- 10GB+ disk space

### Setup:
```bash
# Windows
setup-training.bat

# Linux/Mac
chmod +x setup-training.sh
./setup-training.sh
```

### Train:
```bash
venv-training\Scripts\activate
jupyter notebook notebooks/03_train_model_local.ipynb
```

---

## Troubleshooting

### Out of Memory (OOM)
- Reduce batch size: `per_device_train_batch_size: 8`
- Use gradient accumulation
- Use smaller model variant

### Slow Training
- Use Colab Pro for better GPU
- Reduce dataset size for testing
- Use mixed precision training (fp16)

### Poor Performance
- Increase training epochs
- Add more labeled data
- Try different learning rates