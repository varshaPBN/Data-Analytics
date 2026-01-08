# Windows Installation Guide

If you encounter the error "Failed to build 'pandas' when installing build dependencies", follow these steps:

## Solution 1: Install Pre-built Wheels (Recommended)

This is the easiest solution - it uses pre-compiled packages instead of building from source:

```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install pandas using pre-built wheels only
pip install pandas --only-binary :all:

# Then install the rest of the requirements
pip install -r requirements.txt
```

## Solution 2: Install Microsoft C++ Build Tools

If Solution 1 doesn't work, you need to install the Microsoft C++ Build Tools:

1. **Download Microsoft C++ Build Tools**:
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio"
   - Run the installer

2. **During installation, select**:
   - "C++ build tools" workload
   - Make sure "Windows 10/11 SDK" is checked
   - Click "Install"

3. **Restart your computer** after installation

4. **Try installing again**:
   ```bash
   pip install -r requirements.txt
   ```

## Solution 3: Use Conda (Alternative)

If pip continues to have issues, consider using conda/miniconda:

```bash
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

# Create a new environment
conda create -n data_analytics python=3.12

# Activate environment
conda activate data_analytics

# Install packages
conda install pandas numpy matplotlib
pip install fastapi uvicorn python-multipart sqlalchemy langchain langchain-openai langgraph openai python-dotenv pydantic aiofiles
```

## Solution 4: Install Dependencies Separately

Sometimes installing dependencies in a specific order helps:

```bash
# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install numpy first (pandas dependency)
pip install numpy

# Install pandas
pip install pandas

# Install other dependencies
pip install -r requirements.txt
```

## Solution 5: Use Python 3.12 (Recommended Version)

Python 3.12 is fully supported. If you're using Python 3.12, you're all set:

1. Create a new virtual environment with Python 3.12:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

Note: Python 3.9, 3.10, 3.11, and 3.12 are all supported. Python 3.13+ may have compatibility issues with some packages.

## Quick Fix Script

Run this script to try multiple solutions automatically:

```bash
# Save as fix_install.bat
@echo off
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo Installing numpy first...
pip install numpy

echo Installing pandas with pre-built wheels...
pip install pandas --only-binary :all:

echo Installing remaining requirements...
pip install -r requirements.txt

echo Done!
pause
```

## Still Having Issues?

1. **Check Python version**: 
   ```bash
   python --version
   ```
   Should be 3.9, 3.10, 3.11, or 3.12 (3.13+ may have compatibility issues)

2. **Check pip version**:
   ```bash
   pip --version
   ```
   Should be 23.0 or higher

3. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

4. **Try installing in a fresh virtual environment**:
   ```bash
   python -m venv venv_new
   venv_new\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Common Error Messages and Solutions

### "Microsoft Visual C++ 14.0 or greater is required"
→ Install Microsoft C++ Build Tools (Solution 2)

### "Failed building wheel for pandas"
→ Use `pip install pandas --only-binary :all:` (Solution 1)

### "No module named 'Cython'"
→ Install Cython first: `pip install Cython`, then retry

### "ERROR: Could not build wheels for pandas"
→ Try Solution 1 (pre-built wheels) or Solution 2 (Build Tools)

