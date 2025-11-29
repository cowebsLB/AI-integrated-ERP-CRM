# TinyLlama Setup Instructions

## Where to Place Your TinyLlama Folder

You have **two options** for setting up TinyLlama:

### Option 1: Place in Project Directory (Recommended for Development)

Place your TinyLlama folder **inside the project directory**:

```
AI-integrated-ERP-CRM/
├── tinyllama/          ← Place your TinyLlama folder here
│   ├── config.json
│   ├── tokenizer.json
│   ├── model.safetensors
│   └── ... (other model files)
├── src/
├── main.py
└── ...
```

Then in your `.env` file, set:
```env
TINYLLAMA_PATH=./tinyllama
```

Or use an absolute path:
```env
TINYLLAMA_PATH=C:/Users/COWebs.lb/Desktop/my files/01-Projects/AI-integrated-ERP-CRM/tinyllama
```

### Option 2: Place Anywhere on Your System

Place your TinyLlama folder **anywhere** on your system, for example:

```
C:/models/tinyllama/
```

Then in your `.env` file, set the **full absolute path**:
```env
TINYLLAMA_PATH=C:/models/tinyllama
```

**Windows path format:**
- Use forward slashes: `C:/path/to/tinyllama`
- Or escaped backslashes: `C:\\path\\to\\tinyllama`
- Or raw string format: `r"C:\path\to\tinyllama"` (in Python code)

## Recommended Setup

1. **Create a `models` folder in your project:**
   ```
   AI-integrated-ERP-CRM/
   ├── models/
   │   └── tinyllama/    ← Place here
   ├── src/
   └── ...
   ```

2. **Update your `.env` file:**
   ```env
   TINYLLAMA_PATH=./models/tinyllama
   ```

3. **Or use the existing `models` directory:**
   The project already has a `models/` directory created. You can place TinyLlama there:
   ```
   models/
   └── tinyllama/    ← Place your TinyLlama folder here
   ```
   
   Then set in `.env`:
   ```env
   TINYLLAMA_PATH=./models/tinyllama
   ```

## Folder Structure Expected

Your TinyLlama folder should contain the model files. Typical structure:

```
tinyllama/
├── config.json
├── tokenizer.json
├── tokenizer_config.json
├── model.safetensors (or model.bin)
├── generation_config.json
└── ... (other model files)
```

## Alternative: Use Hugging Face Model Name

If you don't have TinyLlama downloaded locally, the application will automatically download it from Hugging Face if you leave `TINYLLAMA_PATH` empty or use the model name:

```env
TINYLLAMA_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
TINYLLAMA_PATH=
```

The model will be cached in your Hugging Face cache directory (usually `~/.cache/huggingface/`).

## Verification

After setting up, run the application and check the logs. You should see:
```
Loading TinyLlama model from: [your path]
TinyLlama model loaded successfully
```

If you see errors, check:
1. The path in `.env` is correct
2. The folder contains the model files
3. You have read permissions to the folder

## Quick Setup Checklist

- [ ] Place TinyLlama folder in desired location
- [ ] Create/update `.env` file with `TINYLLAMA_PATH`
- [ ] Verify the path is correct (absolute or relative)
- [ ] Run the application to test
- [ ] Check logs for successful model loading

## Example `.env` File

```env
# TinyLlama Configuration
TINYLLAMA_PATH=./models/tinyllama
# Or use absolute path:
# TINYLLAMA_PATH=C:/Users/YourName/Desktop/AI-integrated-ERP-CRM/models/tinyllama

# Database (SQLite - default)
LOCAL_DATABASE_URL=sqlite:///data/erp_crm.db

# Supabase (optional)
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_ENABLED=false
```

## Troubleshooting

**Error: "Model not found"**
- Check the path in `.env` is correct
- Verify the folder exists and contains model files
- Try using an absolute path instead of relative

**Error: "Permission denied"**
- Check file/folder permissions
- Make sure the path is accessible

**Model loads but is slow**
- This is normal for TinyLlama on CPU
- Consider using GPU if available (CUDA)
- The model will be faster after first load (cached)

