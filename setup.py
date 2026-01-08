"""
Setup script for the Data Analytics Agent
"""

import os

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "temp",
        "plots"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

if __name__ == "__main__":
    print("Setting up Data Analytics Agent...")
    create_directories()
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your OPENAI_API_KEY")
    print("2. Install backend dependencies: pip install -r requirements.txt")
    print("3. Install frontend dependencies: cd frontend && npm install")
    print("4. Run backend: python run_backend.py")
    print("5. Run frontend: cd frontend && npm run dev")

