"""
Script to install TinyLlama via Ollama (638MB, Q4_0 quantized).
"""
import subprocess
import sys

print("Installing TinyLlama via Ollama...")
print("This will download the 638MB quantized model.")
print("\nMake sure Ollama is installed from: https://ollama.ai")
print("After installing Ollama, run: ollama pull tinyllama\n")

try:
    import ollama
    print("✓ Ollama Python library is installed")
    
    print("\nPulling tinyllama model (638MB)...")
    print("This may take a few minutes depending on your connection...\n")
    
    ollama.pull("tinyllama")
    
    print("\n✓ TinyLlama installed successfully via Ollama!")
    print("\nYour application is configured to use Ollama.")
    print("Make sure Ollama is running when you use the application.")
    
except ImportError:
    print("Installing Ollama Python library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    
    import ollama
    print("\nPulling tinyllama model...")
    ollama.pull("tinyllama")
    print("\n✓ TinyLlama installed successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease:")
    print("1. Install Ollama from: https://ollama.ai")
    print("2. Make sure Ollama is running")
    print("3. Run: ollama pull tinyllama")
    print("4. Or run this script again")

