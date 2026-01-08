"""
FastAPI Backend for Data Analytics Agent
Main entry point for the API server
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

from .database import init_db, save_dataset, get_dataset
from .agent import DataAnalyticsAgent
from .executor import CodeExecutor
from .models import QueryRequest, QueryResponse

load_dotenv()

app = FastAPI(title="Data Analytics Agent API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Global agent and executor instances (lazy initialization)
agent = None
executor = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent and executor on startup"""
    global agent, executor
    print("Initializing Data Analytics Agent...")
    agent = DataAnalyticsAgent()
    print("Initializing Code Executor...")
    executor = CodeExecutor()
    # Mount static files for serving plots (after executor is created)
    if os.path.exists(executor.temp_dir):
        app.mount("/plots", StaticFiles(directory=executor.temp_dir), name="plots")
    print("✅ Backend ready!")


@app.get("/")
async def root():
    return {"message": "Data Analytics Agent API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file and store it in SQLite
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        contents = await file.read()
        
        # Determine file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload CSV or Excel files."
            )
        
        # Save dataset to database
        dataset_id = await save_dataset(file.filename, contents, file_ext)
        
        return {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "message": "Dataset uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Process a natural language query about the dataset
    """
    try:
        # Check if agent and executor are initialized
        if agent is None or executor is None:
            raise HTTPException(
                status_code=503, 
                detail="Service is still initializing. Please try again in a moment."
            )
        
        # Get dataset from database
        dataset = await get_dataset(request.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Use agent to interpret query and generate code
        code = await agent.generate_code(
            query=request.query,
            dataset_info=dataset['schema_info'],
            sample_data=dataset['sample_data']
        )
        
        # Execute code in sandbox
        result = await executor.execute(
            code=code,
            dataframe_data=dataset['data']
        )
        
        return QueryResponse(**result)
    
    except ValueError as e:
        # Validation or safety error
        return JSONResponse(
            status_code=400,
            content={
                "type": "error",
                "data": str(e),
                "metadata": {"notes": "Query validation failed"}
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "data": str(e),
                "metadata": {"notes": "An error occurred processing your query"}
            }
        )


@app.get("/api/datasets")
async def list_datasets():
    """
    List all uploaded datasets
    """
    try:
        from .database import list_all_datasets
        datasets = await list_all_datasets()
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datasets/{dataset_id}")
async def get_dataset_info(dataset_id: int):
    """
    Get information about a specific dataset
    """
    try:
        dataset = await get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {
            "dataset_id": dataset_id,
            "filename": dataset['filename'],
            "schema_info": dataset['schema_info'],
            "row_count": dataset['row_count']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct execution, use absolute imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

