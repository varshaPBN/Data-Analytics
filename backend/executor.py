"""
Secure code execution sandbox for Pandas analytics
"""

import ast
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import json
import os
import tempfile
from typing import Dict, Any, List, Optional
import traceback
from .sensitive_data import SensitiveDataDetector

# Allowed imports
ALLOWED_IMPORTS = {
    'pandas': pd,
    'numpy': np,
    'matplotlib.pyplot': plt,
    'math': __import__('math'),
    'datetime': __import__('datetime'),
    'json': __import__('json')
}

# Disallowed operations
DISALLOWED_NODES = {
    ast.ImportFrom: lambda node: any(
        name not in ALLOWED_IMPORTS 
        for name in [alias.name if hasattr(alias, 'name') else alias for alias in (node.names or [])]
    ),
    ast.Call: lambda node: any(
        isinstance(node.func, ast.Attribute) and
        hasattr(node.func, 'attr') and
        node.func.attr in ['system', 'popen', 'exec', 'eval', 'compile', '__import__']
    ),
    ast.Import: lambda node: any(
        name.name not in ALLOWED_IMPORTS
        for name in node.names
    )
}

DISALLOWED_NAMES = {
    'os', 'sys', 'subprocess', 'shutil', 'open', 'file', 'exec', 'eval',
    '__import__', 'compile', 'globals', 'locals', 'vars', 'dir'
}


class CodeValidator:
    """Validates Python code for safety"""
    
    @staticmethod
    def validate_code(code: str) -> tuple[bool, str]:
        """
        Validate code for safety
        Returns (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        # Check for disallowed operations
        for node in ast.walk(tree):
            # Check for disallowed imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DISALLOWED_NAMES or alias.name not in ALLOWED_IMPORTS:
                        return False, f"Disallowed import: {alias.name}"
            
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in ALLOWED_IMPORTS:
                    return False, f"Disallowed import from: {node.module}"
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DISALLOWED_NAMES:
                        return False, f"Disallowed function call: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['system', 'popen', 'exec', 'eval']:
                        return False, f"Disallowed method: {node.func.attr}"
            
            # Check for file operations
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['open', 'file']:
                    return False, "File operations are not allowed"
        
        return True, ""
    
    @staticmethod
    def check_for_required_code(code: str) -> bool:
        """Check if code uses the df variable"""
        return 'df' in code


class CodeExecutor:
    """Executes validated Pandas code in a restricted environment"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="analytics_plots_")
        # Ensure directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def execute(
        self, 
        code: str, 
        dataframe_data: str
    ) -> Dict[str, Any]:
        """
        Execute code with dataframe data
        Returns standardized response format
        """
        # Validate code
        is_valid, error_msg = CodeValidator.validate_code(code)
        if not is_valid:
            raise ValueError(f"Code validation failed: {error_msg}")
        
        if not CodeValidator.check_for_required_code(code):
            raise ValueError("Code must use the 'df' variable")
        
        # Load dataframe from JSON
        try:
            df = pd.read_json(dataframe_data, orient='records')
        except Exception as e:
            raise ValueError(f"Failed to load dataframe: {str(e)}")
        
        # Detect and mask sensitive columns before execution
        sensitive_columns = SensitiveDataDetector.get_all_sensitive_columns(list(df.columns))
        df_masked = SensitiveDataDetector.mask_dataframe(df, sensitive_columns)
        
        # Prepare execution environment (use masked dataframe)
        exec_globals = {
            'df': df_masked,
            'pd': pd,
            'np': np,
            'plt': plt,
            'json': json,
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'range': range,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'print': print,
            }
        }
        
        # Execute code
        try:
            exec(code, exec_globals)
        except Exception as e:
            error_trace = traceback.format_exc()
            return {
                "type": "error",
                "data": f"Execution error: {str(e)}",
                "metadata": {
                    "notes": error_trace
                }
            }
        
        # Check for result variable
        result = None
        plot_path = None
        
        # Check if a plot was created
        plot_path = None
        if plt.get_fignums():
            import hashlib
            plot_filename = f"plot_{hashlib.md5(code.encode()).hexdigest()[:8]}.png"
            plot_path = os.path.join(self.temp_dir, plot_filename)
            plt.savefig(plot_path, format='png', dpi=100, bbox_inches='tight')
            plt.close('all')
            # Return relative path for API
            result = {
                "type": "plot",
                "data": f"/plots/{plot_filename}",
                "metadata": {
                    "plot_type": "bar",  # Could be enhanced to detect type
                    "notes": "Chart generated successfully"
                }
            }
        
        # If plot was already set, return it
        if plot_path:
            return result
        
        # Check for common result variable names
        for var_name in ['result', 'output', 'data', 'df_result', 'df_output']:
            if var_name in exec_globals:
                result = exec_globals[var_name]
                break
        
        # If no explicit result, check if df was modified
        if result is None:
            # Try to infer result from last expression
            # This is a simplified approach - in production, you'd parse the AST
            result = df_masked
        
        # Format result (will mask any remaining sensitive columns)
        return self._format_result(result, plot_path, sensitive_columns)
    
    def _format_result(
        self, 
        result: Any, 
        plot_path: Optional[str] = None,
        sensitive_columns: Optional[set] = None
    ) -> Dict[str, Any]:
        """Format execution result into standard response"""
        
        if sensitive_columns is None:
            sensitive_columns = set()
        
        if plot_path:
            return {
                "type": "plot",
                "data": plot_path,
                "metadata": {
                    "plot_type": "bar",
                    "notes": "Chart generated successfully"
                }
            }
        
        if isinstance(result, pd.DataFrame):
            if len(result) == 0:
                return {
                    "type": "text",
                    "data": "No results found",
                    "metadata": {"notes": "Query returned empty dataframe"}
                }
            
            # Mask any sensitive columns that might have been added back
            result = SensitiveDataDetector.mask_dataframe(result, sensitive_columns)
            
            # Limit result size
            if len(result) > 1000:
                result = result.head(1000)
            
            return {
                "type": "table",
                "data": result.to_dict(orient='records'),
                "metadata": {
                    "columns": list(result.columns),
                    "row_count": len(result),
                    "notes": f"Showing {len(result)} rows"
                }
            }
        
        elif isinstance(result, pd.Series):
            # Check if series name is sensitive
            if result.name and result.name in sensitive_columns:
                return {
                    "type": "error",
                    "data": "Access denied: This column contains sensitive data",
                    "metadata": {"notes": "Sensitive data cannot be accessed"}
                }
            
            return {
                "type": "table",
                "data": result.to_dict(),
                "metadata": {
                    "columns": [result.name or "value"],
                    "row_count": len(result),
                    "notes": "Series result"
                }
            }
        
        elif isinstance(result, (int, float, str, bool)):
            return {
                "type": "value",
                "data": result,
                "metadata": {
                    "notes": "Scalar result"
                }
            }
        
        elif isinstance(result, list):
            # Check if it's a list of strings (like column names)
            if len(result) > 0 and all(isinstance(item, str) for item in result):
                # Format as a table with one column
                return {
                    "type": "table",
                    "data": [{"Column Name": col} for col in result],
                    "metadata": {
                        "columns": ["Column Name"],
                        "row_count": len(result),
                        "notes": f"Found {len(result)} columns"
                    }
                }
            else:
                # Regular list - mask sensitive columns if list of dicts
                if len(result) > 0 and isinstance(result[0], dict):
                    masked_data = SensitiveDataDetector.mask_dict_data(result, sensitive_columns)
                else:
                    masked_data = result
                
                return {
                    "type": "table",
                    "data": masked_data,
                    "metadata": {
                        "row_count": len(result),
                        "notes": "List result"
                    }
                }
        
        elif isinstance(result, dict):
            # Mask sensitive columns in dict
            masked_data = {k: ('***MASKED***' if k in sensitive_columns else v) for k, v in result.items()}
            return {
                "type": "table",
                "data": masked_data,
                "metadata": {
                    "row_count": 1,
                    "notes": "Dictionary result"
                }
            }
        
        else:
            return {
                "type": "text",
                "data": str(result),
                "metadata": {
                    "notes": "Result converted to string"
                }
            }

