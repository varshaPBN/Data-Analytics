"""
Sensitive data detection and masking utilities
"""

import re
from typing import List, Dict, Set, Any
import pandas as pd


class SensitiveDataDetector:
    """
    Detects and masks sensitive/PII columns in datasets
    """
    
    # Patterns to identify sensitive column names (case-insensitive)
    SENSITIVE_PATTERNS = {
        # Aadhaar/Identity
        'aadhaar': r'aadhaar|aadhar|uid|unique.*id',
        'pan': r'pan.*card|permanent.*account',
        'passport': r'passport',
        'ssn': r'ssn|social.*security',
        
        # Phone numbers
        'phone': r'phone|mobile|contact.*number|tel|telephone',
        
        # Financial
        'salary': r'salary|wage|income|pay|compensation|earnings',
        'bank': r'bank.*account|account.*number|iban|swift',
        'credit_card': r'credit.*card|debit.*card|card.*number',
        
        # Address
        'address': r'address|location|street|city|pincode|zipcode|postal',
        
        # Personal
        'email': r'email|e-mail|mail',
        'relation': r'relation|relationship|spouse|father|mother|parent',
        'dob': r'date.*birth|dob|birthdate|birth.*date',
        'age': r'age',
        
        # Medical
        'medical': r'medical|health.*record|diagnosis',
        
        # Other PII
        'name': r'^name$|full.*name',  # Only exact match or "full name"
    }
    
    # Additional sensitive keywords in queries
    SENSITIVE_QUERY_KEYWORDS = [
        'aadhaar', 'aadhar', 'phone', 'mobile', 'salary', 'wage', 'income',
        'address', 'email', 'relation', 'relationship', 'spouse', 'father', 'mother',
        'pan', 'passport', 'ssn', 'bank account', 'credit card', 'debit card',
        'date of birth', 'dob', 'age', 'pincode', 'zipcode'
    ]
    
    @classmethod
    def detect_sensitive_columns(cls, columns: List[str]) -> Dict[str, List[str]]:
        """
        Detect sensitive columns based on column names
        Returns dict mapping category to list of column names
        """
        sensitive_columns = {}
        
        for category, pattern in cls.SENSITIVE_PATTERNS.items():
            matches = []
            for col in columns:
                col_lower = col.lower().strip()
                if re.search(pattern, col_lower, re.IGNORECASE):
                    matches.append(col)
            if matches:
                sensitive_columns[category] = matches
        
        return sensitive_columns
    
    @classmethod
    def get_all_sensitive_columns(cls, columns: List[str]) -> Set[str]:
        """
        Get all sensitive column names as a set
        """
        sensitive_dict = cls.detect_sensitive_columns(columns)
        all_sensitive = set()
        for cols in sensitive_dict.values():
            all_sensitive.update(cols)
        return all_sensitive
    
    @classmethod
    def mask_dataframe(cls, df: pd.DataFrame, sensitive_columns: Set[str] = None) -> pd.DataFrame:
        """
        Mask sensitive columns in a DataFrame
        """
        if sensitive_columns is None:
            sensitive_columns = cls.get_all_sensitive_columns(list(df.columns))
        
        df_masked = df.copy()
        
        for col in sensitive_columns:
            if col in df_masked.columns:
                # Mask with asterisks, keeping first/last characters for some types
                if df_masked[col].dtype == 'object':  # String columns
                    df_masked[col] = df_masked[col].apply(
                        lambda x: '***MASKED***' if pd.notna(x) and str(x).strip() else x
                    )
                else:  # Numeric columns (salary, etc.)
                    df_masked[col] = '***MASKED***'
        
        return df_masked
    
    @classmethod
    def mask_dict_data(cls, data: List[Dict[str, Any]], sensitive_columns: Set[str]) -> List[Dict[str, Any]]:
        """
        Mask sensitive columns in a list of dictionaries
        """
        masked_data = []
        for row in data:
            masked_row = row.copy()
            for col in sensitive_columns:
                if col in masked_row:
                    masked_row[col] = '***MASKED***'
            masked_data.append(masked_row)
        return masked_data
    
    @classmethod
    def check_query_for_sensitive_data(cls, query: str) -> tuple[bool, str]:
        """
        Check if a query is asking for sensitive data
        Returns (is_sensitive, reason)
        """
        query_lower = query.lower()
        
        # Check for sensitive keywords
        for keyword in cls.SENSITIVE_QUERY_KEYWORDS:
            if keyword in query_lower:
                return True, f"Query contains sensitive data request: '{keyword}'"
        
        # Check for patterns like "show me phone numbers", "list salaries", etc.
        sensitive_verbs = ['show', 'list', 'display', 'get', 'find', 'return', 'give']
        for verb in sensitive_verbs:
            for keyword in cls.SENSITIVE_QUERY_KEYWORDS:
                pattern = f"{verb}.*{keyword}|{keyword}.*{verb}"
                if re.search(pattern, query_lower):
                    return True, f"Query requests sensitive data: '{keyword}'"
        
        return False, ""
    
    @classmethod
    def check_code_for_sensitive_columns(cls, code: str, sensitive_columns: Set[str]) -> tuple[bool, str]:
        """
        Check if generated code accesses sensitive columns
        Returns (is_sensitive, reason)
        """
        code_lower = code.lower()
        
        for col in sensitive_columns:
            col_lower = col.lower()
            # Check if column is accessed in code
            # Look for patterns like df['column'], df.column, df[['column']], etc.
            patterns = [
                f"df\\['{re.escape(col)}'\\]",
                f'df\\["{re.escape(col)}"\\]',
                f"df\\.{re.escape(col)}",
                f"\\['{re.escape(col)}'\\]",
                f'\\["{re.escape(col)}"\\]',
            ]
            
            for pattern in patterns:
                if re.search(pattern, code_lower):
                    return True, f"Code attempts to access sensitive column: '{col}'"
        
        return False, ""

