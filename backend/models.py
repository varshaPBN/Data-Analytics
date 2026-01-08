"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal


class QueryRequest(BaseModel):
    """Request model for natural language queries"""
    dataset_id: int
    query: str


class QueryResponse(BaseModel):
    """Response model for query results"""
    type: Literal["table", "value", "plot", "text", "error"]
    data: Any  # Can be dict, list, str, or file path
    metadata: Dict[str, Any] = {
        "columns": [],
        "row_count": 0,
        "plot_type": "none",
        "notes": ""
    }

