# Ollama Setup Instructions

## Quick Setup for TinyLlama (638MB)

### Step 1: Install Ollama Desktop App

1. **Download Ollama:**
   - Go to: https://ollama.ai
   - Download the Windows installer
   - Run the installer and follow the setup wizard

2. **Verify Installation:**
   - Ollama should start automatically
   - You can verify it's running by opening a terminal and running:
     ```bash
     ollama --version
     ```

### Step 2: Pull TinyLlama Model

Once Ollama is installed and running, pull the model:

```bash
ollama pull tinyllama
```

This will download the 638MB quantized TinyLlama model.

### Step 3: Verify Model is Installed

Check that the model is available:

```bash
ollama list
```

You should see `tinyllama` in the list.

### Step 4: Test the Model

Test that it works:

```bash
ollama run tinyllama "Hello, how are you?"
```

### Step 5: Configure Application

The application is already configured to use Ollama by default. No additional configuration needed!

If you want to customize, add to your `.env` file:
```env
USE_OLLAMA=true
OLLAMA_MODEL=tinyllama
```

## Troubleshooting

**Ollama not found:**
- Make sure Ollama is installed and running
- Check that Ollama is in your PATH
- Restart your terminal/IDE after installing

**Connection error:**
- Make sure Ollama service is running
- Check if Ollama is accessible: `ollama list`
- Try restarting Ollama

**Model not found:**
- Run: `ollama pull tinyllama`
- Wait for download to complete
- Verify with: `ollama list`

## Alternative: Use Python Script

You can also use the provided script:

```bash
python install_ollama_tinyllama.py
```

This will automatically pull the model if Ollama is running.

## Benefits of Ollama

- ✅ **Smaller size:** 638MB vs 2.2GB
- ✅ **Faster:** Quantized model runs faster
- ✅ **Easy management:** Simple commands to manage models
- ✅ **Automatic updates:** Easy to update models
- ✅ **Multiple models:** Can easily switch between different models

