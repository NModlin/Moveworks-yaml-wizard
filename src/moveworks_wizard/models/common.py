"""
Common data structures used across different Compound Action constructs.
"""

from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator


class InputArg(BaseModel):
    """
    Represents an input argument for a Compound Action or individual step.
    
    Input arguments use Moveworks Data Mapping (Bender) syntax for dynamic values.
    """
    
    name: str = Field(..., description="Name of the input argument")
    value: Any = Field(..., description="Value using Bender syntax (e.g., 'data.user_id')")
    description: Optional[str] = Field(None, description="Human-readable description")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {self.name: self.value}


class DelayConfig(BaseModel):
    """
    Configuration for delays before executing an action.
    
    Supports various time units with DSL expressions.
    """
    
    milliseconds: Optional[Union[str, int]] = Field(None, description="Delay in milliseconds")
    seconds: Optional[Union[str, int]] = Field(None, description="Delay in seconds") 
    minutes: Optional[Union[str, int]] = Field(None, description="Delay in minutes")
    hours: Optional[Union[str, int]] = Field(None, description="Delay in hours")
    days: Optional[Union[str, int]] = Field(None, description="Delay in days")
    
    @field_validator('milliseconds', 'seconds', 'minutes', 'hours', 'days', mode='before')
    @classmethod
    def validate_delay_values(cls, v):
        """Ensure delay values are either integers or DSL expression strings."""
        if v is not None:
            if isinstance(v, int) and v < 0:
                raise ValueError("Delay values must be non-negative")
            elif isinstance(v, str):
                # For DSL expressions, we'll do basic validation
                if not v.strip():
                    raise ValueError("DSL expressions cannot be empty")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        for field_name, field_value in self.model_dump(exclude_none=True).items():
            if field_value is not None:
                # Convert integers to strings as required by Moveworks
                result[field_name] = str(field_value) if isinstance(field_value, int) else field_value
        return result


class ProgressUpdates(BaseModel):
    """
    Configuration for progress update messages during action execution.
    
    Used to provide user feedback during long-running operations.
    """
    
    on_pending: Optional[str] = Field(None, description="Message shown while action is pending")
    on_complete: Optional[str] = Field(None, description="Message shown when action completes")
    
    @field_validator('on_pending', 'on_complete')
    @classmethod
    def validate_messages(cls, v):
        """Ensure messages are non-empty if provided."""
        if v is not None and not v.strip():
            raise ValueError("Progress update messages cannot be empty")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return self.model_dump(exclude_none=True)


class BenderExpression(BaseModel):
    """
    Represents a Moveworks Data Mapping (Bender) expression.
    
    This is a wrapper for Bender syntax expressions used throughout
    Compound Actions for dynamic data access and manipulation.
    """
    
    expression: str = Field(..., description="The Bender expression")
    
    @field_validator('expression')
    @classmethod
    def validate_expression(cls, v):
        """Basic validation for Bender expressions."""
        if not v.strip():
            raise ValueError("Bender expressions cannot be empty")
        return v.strip()
    
    def __str__(self) -> str:
        """Return the expression string for YAML serialization."""
        return self.expression
    
    @classmethod
    def from_string(cls, expr: str) -> 'BenderExpression':
        """Create a BenderExpression from a string."""
        return cls(expression=expr)


class ActionReference(BaseModel):
    """
    Represents a reference to a Moveworks action (HTTP, Built-in, etc.).
    """
    
    action_name: str = Field(..., description="Unique identifier for the action")
    is_builtin: bool = Field(False, description="Whether this is a built-in Moveworks action")
    
    @field_validator('action_name')
    @classmethod
    def validate_action_name(cls, v):
        """Validate action name format."""
        if not v.strip():
            raise ValueError("Action name cannot be empty")

        # Built-in actions should start with 'mw.'
        if v.startswith('mw.'):
            return v

        # For non-builtin actions, ensure it's a valid identifier
        # This could be a UUID or other identifier format
        return v.strip()
    
    @property
    def is_moveworks_builtin(self) -> bool:
        """Check if this is a Moveworks built-in action."""
        return self.action_name.startswith('mw.')
    
    def __str__(self) -> str:
        """Return the action name for YAML serialization."""
        return self.action_name
