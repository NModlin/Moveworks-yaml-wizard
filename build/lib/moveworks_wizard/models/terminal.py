"""
Models for terminal steps in Compound Actions.

This includes return and raise steps that end compound action execution.
"""

from typing import Any, Dict, Optional
from pydantic import Field, field_validator

from .base import BaseStep


class ReturnStep(BaseStep):
    """
    Represents a return step that ends the compound action gracefully.
    
    Returns structured data using the output_mapper with Moveworks
    Data Mapping syntax.
    """
    
    output_mapper: Optional[Dict[str, Any]] = Field(
        None,
        description="Mapping of output variables using Bender syntax"
    )
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "return"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this return step to YAML dictionary format."""
        return_dict = {}
        
        if self.output_mapper:
            return_dict["output_mapper"] = self.output_mapper
        
        return {"return": return_dict}


class RaiseStep(BaseStep):
    """
    Represents a raise step that stops the compound action with an error.
    
    Used for error handling and early exit when error conditions are met.
    """
    
    output_key: str = Field(..., description="Variable name to store error information")
    message: Optional[str] = Field(None, description="Error message to display")
    
    @field_validator('output_key')
    @classmethod
    def validate_output_key(cls, v):
        """Validate output key format."""
        if not v.strip():
            raise ValueError("Output key cannot be empty")

        # Output key should be a valid variable name
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Output key must be alphanumeric with underscores/hyphens")

        return v.strip()

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate error message."""
        if v is not None and not v.strip():
            raise ValueError("Error message cannot be empty if provided")
        return v
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "raise"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this raise step to YAML dictionary format."""
        raise_dict = {
            "output_key": self.output_key
        }
        
        if self.message:
            raise_dict["message"] = self.message
        
        return {"raise": raise_dict}
