@echo off
echo ========================================
echo Data Analytics Agent - Installation Fix
echo ========================================
echo.

echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

echo.
echo Step 2: Installing numpy first (pandas dependency)...
pip install numpy
if errorlevel 1 (
    echo ERROR: Failed to install numpy
    pause
    exit /b 1
)

echo.
echo Step 3: Installing pandas with pre-built wheels...
pip install pandas --only-binary :all:
if errorlevel 1 (
    echo WARNING: Failed to install pandas with pre-built wheels
    echo You may need to install Microsoft C++ Build Tools
    echo See INSTALL_WINDOWS.md for details
)

echo.
echo Step 4: Installing remaining requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Some packages failed to install
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file with your OPENAI_API_KEY
echo 2. Run: python run_backend.py
echo.
pause

