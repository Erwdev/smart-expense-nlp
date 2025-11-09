# Notebooks Directory

## Training Workflow

### Local Development:
1. `01_data_exploration.ipynb` - Explore & visualize dataset
2. `02_data_preprocessing.ipynb` - Clean & tokenize data
3. `03_train_model_local.ipynb` - Train on local machine
4. `04_evaluation.ipynb` - Evaluate model performance
5. `05_export_model.ipynb` - Export for production

### Google Colab (Recommended):
- `train_on_colab.ipynb` - All-in-one training script for Colab

## Setup

### Local:
```bash
venv\Scripts\activate
jupyter notebook
```

### Colab:
1. Upload `train_on_colab.ipynb` to Google Drive
2. Open with Google Colab
3. Runtime → Change runtime type → GPU (T4)
4. Run all cells