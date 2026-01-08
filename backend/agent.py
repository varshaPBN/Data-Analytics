"""
LangGraph agent for natural language query interpretation and code generation
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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
    
    async def generate_code(
        self,
        query: str,
        dataset_info: Dict[str, Any],
        sample_data: list
    ) -> str:
        """
        Generate safe Pandas code from natural language query
        """
        
        system_prompt = """You are a specialized data analytics code generator. 
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

Dataset Schema:
{schema_info}

Sample Data (first 5 rows):
{sample_data}

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
        
        # Format prompt with dataset info
        formatted_prompt = prompt.format_messages(
            schema_info=json.dumps(dataset_info, indent=2),
            sample_data=json.dumps(sample_data, indent=2)
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

