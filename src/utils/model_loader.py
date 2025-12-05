import os
import gdown
import zipfile
import shutil
from pathlib import Path

class ModelLoader:
    REQUIRED_MODEL_FILES = [
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt"
    ]

    def __init__(self, gdrive_file_id: str, model_dir: str):
        self.gdrive_file_id = gdrive_file_id
        self.model_dir = Path(model_dir)
        self.zip_path = self.model_dir.parent / "model.zip"

    # -------------------------------------------------------------
    # Check model completeness
    # -------------------------------------------------------------
    def model_exists(self):
        return all((self.model_dir / f).exists() for f in self.REQUIRED_MODEL_FILES)

    # -------------------------------------------------------------
    # Check zip validity
    # -------------------------------------------------------------
    def zip_valid(self):
        if not self.zip_path.exists():
            return False
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                return z.testzip() is None
        except:
            return False

    # -------------------------------------------------------------
    # Download zip (if needed)
    # -------------------------------------------------------------
    def download(self):
        if self.zip_valid():
            print("[MODEL] ✓ ZIP already exists, skipping download.")
            return True

        print("[MODEL] Downloading model from Google Drive...")
        try:
            url = f"https://drive.google.com/uc?id={self.gdrive_file_id}"
            gdown.download(url, str(self.zip_path), quiet=False)
            return self.zip_valid()
        except Exception as e:
            print(f"[MODEL] ✗ Download failed: {e}")
            return False

    # -------------------------------------------------------------
    # Extract (only if model not already available)
    # -------------------------------------------------------------
    def extract(self):
        if self.model_exists():
            print("[MODEL] ✓ Model already extracted. Skipping extract.")
            return True

        if not self.zip_valid():
            print("[MODEL] ✗ ZIP not found or invalid.")
            return False

        print("[MODEL] Extracting ZIP...")
        try:
            temp = self.model_dir.parent / "temp_extract"
            if temp.exists():
                shutil.rmtree(temp)
            temp.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.zip_path, 'r') as z:
                z.extractall(temp)

            # Move extracted model
            extracted_dirs = list(temp.glob("**/config.json"))
            if not extracted_dirs:
                print("[MODEL] ✗ Could not find model files inside ZIP.")
                return False

            model_root = extracted_dirs[0].parent

            if self.model_dir.exists():
                shutil.rmtree(self.model_dir)
            shutil.copytree(model_root, self.model_dir)

            shutil.rmtree(temp)
            return True

        except Exception as e:
            print(f"[MODEL] ✗ Extraction failed: {e}")
            return False

    # -------------------------------------------------------------
    # MAIN LOAD FUNCTION
    # -------------------------------------------------------------
    def load(self):
        print("[MODEL] Checking model...")

        # 1. If model fully exists → skip everything
        if self.model_exists():
            print("[MODEL] ✓ Model already exists. No download needed.")
            return True

        # 2. Try download
        if not self.download():
            if self.model_exists():
                print("[MODEL] ⚠ Download failed but model exists → proceeding.")
                return True
            print("[MODEL] ✗ Download failed and model missing → cannot continue.")
            return False

        # 3. Extract
        if not self.extract():
            if self.model_exists():
                print("[MODEL] ⚠ Extract failed but model exists → proceeding.")
                return True
            print("[MODEL] ✗ Extraction failed and model missing → cannot continue.")
            return False

        print("[MODEL] ✓ Model ready.")
        return True
