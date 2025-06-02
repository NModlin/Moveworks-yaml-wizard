"""
Bender (Moveworks Data Mapping Language) assistant for creating data mapping expressions.

This module provides assistance for creating Bender expressions used in
Compound Action input_args and output_mappers.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class BenderFunctionType(Enum):
    """Types of Bender functions available."""
    MAP = "MAP"
    CONCAT = "CONCAT"
    RENDER = "RENDER"
    FILTER = "FILTER"
    EXTRACT = "EXTRACT"
    TRANSFORM = "TRANSFORM"
    CONDITIONAL = "CONDITIONAL"
    ARITHMETIC = "ARITHMETIC"


@dataclass
class BenderFunction:
    """Represents a Bender function with its parameters."""
    name: str
    description: str
    function_type: BenderFunctionType
    parameters: List[str]
    example: str
    use_case: str


@dataclass
class BenderExpression:
    """Represents a complete Bender expression."""
    expression: str
    description: str
    data_sources: List[str]
    output_type: str


class BenderAssistant:
    """
    Assistant for creating Bender (Moveworks Data Mapping Language) expressions.
    
    Provides guidance and templates for common data mapping scenarios.
    """
    
    def __init__(self):
        """Initialize the Bender assistant."""
        self._functions = self._load_bender_functions()
        self._common_patterns = self._load_common_patterns()
    
    def _load_bender_functions(self) -> Dict[str, BenderFunction]:
        """Load available Bender functions."""
        functions = {}
        
        # MAP function
        functions["MAP"] = BenderFunction(
            name="MAP",
            description="Transform each element in an array using an expression",
            function_type=BenderFunctionType.MAP,
            parameters=["array", "expression"],
            example="MAP(data.users, 'user.name')",
            use_case="Extract specific fields from arrays of objects"
        )
        
        # CONCAT function
        functions["CONCAT"] = BenderFunction(
            name="CONCAT",
            description="Concatenate multiple strings or values",
            function_type=BenderFunctionType.CONCAT,
            parameters=["value1", "value2", "..."],
            example="CONCAT(data.first_name, ' ', data.last_name)",
            use_case="Combine multiple data fields into a single string"
        )
        
        # RENDER function
        functions["RENDER"] = BenderFunction(
            name="RENDER",
            description="Render a template string with variable substitution",
            function_type=BenderFunctionType.RENDER,
            parameters=["template", "data"],
            example="RENDER('Hello {{name}}, your ticket is {{ticket_id}}', data)",
            use_case="Create formatted messages with dynamic content"
        )
        
        # FILTER function
        functions["FILTER"] = BenderFunction(
            name="FILTER",
            description="Filter array elements based on a condition",
            function_type=BenderFunctionType.FILTER,
            parameters=["array", "condition"],
            example="FILTER(data.tickets, 'ticket.priority == \"high\"')",
            use_case="Select specific items from arrays based on criteria"
        )
        
        # EXTRACT function
        functions["EXTRACT"] = BenderFunction(
            name="EXTRACT",
            description="Extract data using regex or pattern matching",
            function_type=BenderFunctionType.EXTRACT,
            parameters=["text", "pattern"],
            example="EXTRACT(data.email, '@(.+)')",
            use_case="Parse specific parts of text data"
        )
        
        # Conditional expressions
        functions["IF"] = BenderFunction(
            name="IF",
            description="Conditional expression (ternary operator)",
            function_type=BenderFunctionType.CONDITIONAL,
            parameters=["condition", "true_value", "false_value"],
            example="IF(data.priority == 'high', 'urgent', 'normal')",
            use_case="Choose values based on conditions"
        )
        
        return functions
    
    def _load_common_patterns(self) -> Dict[str, BenderExpression]:
        """Load common Bender expression patterns."""
        patterns = {}
        
        # User information extraction
        patterns["user_full_name"] = BenderExpression(
            expression="CONCAT(data.user_info.first_name, ' ', data.user_info.last_name)",
            description="Combine first and last name into full name",
            data_sources=["data.user_info.first_name", "data.user_info.last_name"],
            output_type="string"
        )
        
        # Email domain extraction
        patterns["email_domain"] = BenderExpression(
            expression="EXTRACT(data.user_email, '@(.+)')",
            description="Extract domain from email address",
            data_sources=["data.user_email"],
            output_type="string"
        )
        
        # Priority-based message
        patterns["priority_message"] = BenderExpression(
            expression="IF(data.ticket_priority == 'critical', 'URGENT: Immediate attention required', 'Standard processing')",
            description="Generate message based on ticket priority",
            data_sources=["data.ticket_priority"],
            output_type="string"
        )
        
        # User notification template
        patterns["user_notification"] = BenderExpression(
            expression="RENDER('Hello {{user_name}}, your request {{request_id}} has been {{status}}.', data)",
            description="Personalized notification message template",
            data_sources=["data.user_name", "data.request_id", "data.status"],
            output_type="string"
        )
        
        # Manager list extraction
        patterns["manager_emails"] = BenderExpression(
            expression="MAP(data.managers, 'manager.email')",
            description="Extract email addresses from manager list",
            data_sources=["data.managers"],
            output_type="array"
        )
        
        # Active users filter
        patterns["active_users"] = BenderExpression(
            expression="FILTER(data.users, 'user.status == \"active\"')",
            description="Filter for only active users",
            data_sources=["data.users"],
            output_type="array"
        )
        
        return patterns
    
    def get_function(self, function_name: str) -> Optional[BenderFunction]:
        """Get information about a specific Bender function."""
        return self._functions.get(function_name.upper())
    
    def get_functions_by_type(self, function_type: BenderFunctionType) -> List[BenderFunction]:
        """Get all functions of a specific type."""
        return [func for func in self._functions.values() if func.function_type == function_type]
    
    def get_all_functions(self) -> List[BenderFunction]:
        """Get all available Bender functions."""
        return list(self._functions.values())
    
    def get_pattern(self, pattern_name: str) -> Optional[BenderExpression]:
        """Get a common expression pattern."""
        return self._common_patterns.get(pattern_name)
    
    def get_all_patterns(self) -> List[BenderExpression]:
        """Get all common expression patterns."""
        return list(self._common_patterns.values())
    
    def search_functions(self, query: str) -> List[BenderFunction]:
        """Search for functions by name, description, or use case."""
        query = query.lower()
        results = []
        
        for function in self._functions.values():
            if (query in function.name.lower() or 
                query in function.description.lower() or
                query in function.use_case.lower()):
                results.append(function)
        
        return results
    
    def search_patterns(self, query: str) -> List[BenderExpression]:
        """Search for patterns by description or data sources."""
        query = query.lower()
        results = []
        
        for pattern in self._common_patterns.values():
            if (query in pattern.description.lower() or
                any(query in source.lower() for source in pattern.data_sources)):
                results.append(pattern)
        
        return results
    
    def suggest_expression(self, use_case: str, data_sources: List[str]) -> List[BenderExpression]:
        """Suggest Bender expressions based on use case and available data."""
        suggestions = []
        use_case_lower = use_case.lower()
        
        # Simple keyword-based suggestions
        if "name" in use_case_lower and any("first_name" in source for source in data_sources):
            suggestions.append(self._common_patterns["user_full_name"])
        
        if "email" in use_case_lower and any("email" in source for source in data_sources):
            suggestions.append(self._common_patterns["email_domain"])
        
        if "notification" in use_case_lower or "message" in use_case_lower:
            suggestions.append(self._common_patterns["user_notification"])
        
        if "priority" in use_case_lower:
            suggestions.append(self._common_patterns["priority_message"])
        
        if "manager" in use_case_lower and any("managers" in source for source in data_sources):
            suggestions.append(self._common_patterns["manager_emails"])
        
        if "filter" in use_case_lower or "active" in use_case_lower:
            suggestions.append(self._common_patterns["active_users"])
        
        return suggestions
    
    def validate_expression(self, expression: str) -> Dict[str, Any]:
        """Basic validation of Bender expression syntax."""
        errors = []
        warnings = []
        
        # Check for balanced parentheses
        paren_count = expression.count('(') - expression.count(')')
        if paren_count != 0:
            errors.append("Unbalanced parentheses")
        
        # Check for known function names
        import re
        function_calls = re.findall(r'([A-Z_]+)\s*\(', expression)
        for func_name in function_calls:
            if func_name not in self._functions:
                warnings.append(f"Unknown function: {func_name}")
        
        # Check for data references
        if not re.search(r'data\.|meta_info\.', expression):
            warnings.append("Expression doesn't reference data sources")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'functions_used': function_calls
        }


# Global Bender assistant instance
bender_assistant = BenderAssistant()
