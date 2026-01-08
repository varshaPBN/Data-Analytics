"""
Entry point for running the FastAPI backend
Run with: python run_backend.py
"""

import uvicorn
import os
import sys

# Add project root to path so backend can be imported as a package
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure we're in the project root directory
os.chdir(project_root)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[os.path.join(project_root, "backend")],  # Only watch backend directory
        reload_excludes=["venv/**", "*.pyc", "__pycache__/**"]  # Exclude venv and cache files
    )

