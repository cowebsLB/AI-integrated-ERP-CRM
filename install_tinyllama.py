"""
Script to download and install TinyLlama model (smallest/quantized version).
"""
import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
TINYLLAMA_DIR = MODELS_DIR / "tinyllama"

# Create models directory if it doesn't exist
MODELS_DIR.mkdir(exist_ok=True)

print("Downloading TinyLlama model (smallest available)...")
print(f"Target directory: {TINYLLAMA_DIR}")

try:
    from huggingface_hub import snapshot_download
    
    # Try to download - it will resume if interrupted
    print("\nDownloading TinyLlama-1.1B-Chat-v1.0 (~800MB)...")
    print("Note: This is the smallest official TinyLlama model.")
    print("Download can be resumed if interrupted.\n")
    
    snapshot_download(
        repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        local_dir=str(TINYLLAMA_DIR),
        resume_download=True  # Resume if interrupted
    )
    
    print(f"\n✓ TinyLlama downloaded successfully!")
    print(f"✓ Model location: {TINYLLAMA_DIR}")
    print(f"\nNext steps:")
    print(f"1. Update your .env file with: TINYLLAMA_PATH=./models/tinyllama")
    print(f"2. Or use absolute path: TINYLLAMA_PATH={TINYLLAMA_DIR}")
    
except ImportError:
    print("huggingface_hub not found. Installing...")
    import subprocess
    subprocess.check_call(["python", "-m", "pip", "install", "huggingface_hub"])
    
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        local_dir=str(TINYLLAMA_DIR),
        resume_download=True
    )
    print(f"\n✓ TinyLlama downloaded successfully!")
    
except Exception as e:
    print(f"\n✗ Error downloading TinyLlama: {e}")
    print("\nTrying alternative: Using transformers to download...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("Downloading using transformers (will cache in Hugging Face cache)...")
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=str(TINYLLAMA_DIR),
            resume_download=True
        )
        tokenizer.save_pretrained(str(TINYLLAMA_DIR))
        
        print("Downloading model (this may take a while, ~800MB)...")
        print("You can interrupt and resume later - it will continue from where it left off.")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=str(TINYLLAMA_DIR),
            resume_download=True,
            torch_dtype="float16"  # Use half precision to save space
        )
        model.save_pretrained(str(TINYLLAMA_DIR))
        
        print(f"\n✓ TinyLlama downloaded successfully!")
        print(f"✓ Model location: {TINYLLAMA_DIR}")
        print(f"\nUpdate your .env file with: TINYLLAMA_PATH=./models/tinyllama")
        
    except Exception as e2:
        print(f"\n✗ Error: {e2}")
        print("\nAlternative: You can manually download from:")
        print("  https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        print(f"\nAnd place the files in: {TINYLLAMA_DIR}")
