"""
LangGraph agent for natural language query interpretation and code generation
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from opik import track
import opik
from .sensitive_data import SensitiveDataDetector
import json


class DataAnalyticsAgent:
    """
    Agent that interprets natural language queries and generates Pandas code
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
        
        # Initialize Opik for LLM tracing
        # OPIK_API_KEY should be set in environment variables
        # Get your API key from: https://comet.com/opik/your-workspace-name/get-started
        opik.init()
    
    @track
    async def generate_code(
        self,
        query: str,
        dataset_info: Dict[str, Any],
        sample_data: list
    ) -> str:
        """
        Generate safe Pandas code from natural language query
        """
        
        # Check for sensitive data requests
        is_sensitive, reason = SensitiveDataDetector.check_query_for_sensitive_data(query)
        if is_sensitive:
            raise ValueError(f"Access denied: {reason}. Sensitive data cannot be accessed.")
        
        # Detect sensitive columns
        columns = dataset_info.get('columns', [])
        sensitive_columns = SensitiveDataDetector.get_all_sensitive_columns(columns)
        
        # Filter out sensitive columns from sample data
        safe_sample_data = []
        for row in sample_data:
            safe_row = {k: v for k, v in row.items() if k not in sensitive_columns}
            safe_sample_data.append(safe_row)
        
        # Create safe schema info (exclude sensitive columns)
        safe_columns = [col for col in columns if col not in sensitive_columns]
        safe_schema_info = {
            "columns": safe_columns,
            "dtypes": {k: v for k, v in dataset_info.get('dtypes', {}).items() if k not in sensitive_columns},
            "shape": dataset_info.get('shape', (0, 0))
        }
        
        # Add sensitive data warning to prompt
        sensitive_warning = ""
        if sensitive_columns:
            sensitive_warning = f"\n\nSECURITY WARNING: The following columns contain sensitive data and MUST NOT be accessed: {', '.join(sorted(sensitive_columns))}\nYou MUST NOT generate code that accesses these columns. If the query asks for this data, raise an error or return a message that this data is protected."
        
        system_prompt = f"""You are a specialized data analytics code generator. 
Your task is to convert natural language questions about tabular data into correct, safe, and minimal Pandas code.

CRITICAL RULES:
1. You MUST use only the 'df' variable (it's already loaded as a pandas DataFrame)
2. You can ONLY import: pandas (as pd), numpy (as np), matplotlib.pyplot (as plt), math, datetime, json
3. You CANNOT use: os, sys, subprocess, shutil, file operations, network calls, plt.show()
4. Your code must be self-contained and assume 'df' exists
5. If generating a plot, you MUST save it with plt.savefig() - NEVER use plt.show()
6. Store your final result in a variable named 'result'
7. Keep code minimal and focused on the query
8. For aggregations, use .agg() or .sum(), .mean(), etc.
9. For filtering, use boolean indexing: df[df['column'] > value]
10. For sorting, use .sort_values()
11. For grouping, use .groupby()
{sensitive_warning}

Dataset Schema (only non-sensitive columns):
{{schema_info}}

Sample Data (first 5 rows, sensitive columns excluded):
{{sample_data}}

IMPORTANT: Generate ONLY the Python code. Do NOT include markdown code blocks, explanations, or comments. Just the raw Python code."""

        user_prompt = f"""User Query: {query}

Generate Pandas code to answer this question. 

Requirements:
- Use the 'df' variable (already loaded as a DataFrame)
- Store the final result in a variable named 'result'
- For plots, use plt.savefig() to save (do NOT use plt.show())
- Code must be safe and use only allowed libraries (pandas, numpy, matplotlib.pyplot, math, datetime, json)
- Make sure the code directly answers the user's question"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        # Format prompt with safe dataset info (sensitive columns excluded)
        formatted_prompt = prompt.format_messages(
            schema_info=json.dumps(safe_schema_info, indent=2),
            sample_data=json.dumps(safe_sample_data, indent=2)
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        
        # Extract code from response
        code = response.content.strip()
        
        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        
        # Validate that code doesn't access sensitive columns
        is_sensitive, reason = SensitiveDataDetector.check_code_for_sensitive_columns(code, sensitive_columns)
        if is_sensitive:
            raise ValueError(f"Security violation: {reason}")
        
        return code
    
    def _validate_query(self, query: str) -> tuple[bool, str]:
        """Basic query validation"""
        if not query or len(query.strip()) < 3:
            return False, "Query is too short"
        
        # Check for potentially malicious patterns
        dangerous_patterns = [
            'import os', 'import sys', 'subprocess', 'exec(', 'eval(',
            '__import__', 'open(', 'file(', 'system('
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                return False, f"Query contains disallowed pattern: {pattern}"
        
        return True, ""

