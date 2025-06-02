"""
Models for action-based steps in Compound Actions.

This includes HTTP actions, Script actions (APIthon), and Built-in actions.
"""

from typing import Any, Dict, Optional
from pydantic import Field, field_validator

from .base import BaseStep
from .common import DelayConfig, ProgressUpdates, ActionReference


class ActionStep(BaseStep):
    """
    Represents an action step in a Compound Action.
    
    Actions can be HTTP requests, built-in Moveworks actions, or other
    external system integrations.
    """
    
    action_name: str = Field(..., description="Unique identifier for the action to execute")
    output_key: str = Field(..., description="Variable name to store the action result")
    input_args: Optional[Dict[str, Any]] = Field(
        None, 
        description="Input arguments for the action using Bender syntax"
    )
    delay_config: Optional[DelayConfig] = Field(
        None,
        description="Configuration for delays before executing this action"
    )
    progress_updates: Optional[ProgressUpdates] = Field(
        None,
        description="Progress update messages for user feedback"
    )
    
    @field_validator('action_name')
    @classmethod
    def validate_action_name(cls, v):
        """Validate action name format."""
        if not v.strip():
            raise ValueError("Action name cannot be empty")
        return v.strip()

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
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "action"
    
    def is_builtin_action(self) -> bool:
        """Check if this is a Moveworks built-in action."""
        return self.action_name.startswith('mw.')
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this action step to YAML dictionary format."""
        action_dict = {
            "action_name": self.action_name,
            "output_key": self.output_key
        }
        
        # Add optional fields if present
        if self.input_args:
            action_dict["input_args"] = self.input_args
        
        if self.delay_config:
            action_dict["delay_config"] = self.delay_config.to_dict()
        
        if self.progress_updates:
            action_dict["progress_updates"] = self.progress_updates.to_dict()
        
        return {"action": action_dict}


class ScriptStep(BaseStep):
    """
    Represents a script step in a Compound Action.
    
    Scripts use APIthon (Python-based scripting language) for custom logic,
    data manipulation, or computations.
    """
    
    code: str = Field(..., description="The APIthon (Python) code to execute")
    output_key: str = Field(..., description="Variable name to store the script result")
    input_args: Optional[Dict[str, Any]] = Field(
        None,
        description="Input arguments for the script using Bender syntax"
    )
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        """Validate script code."""
        if not v.strip():
            raise ValueError("Script code cannot be empty")
        return v.strip()

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
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "script"
    
    def is_multiline_code(self) -> bool:
        """Check if the code contains multiple lines."""
        return '\n' in self.code
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this script step to YAML dictionary format."""
        script_dict = {
            "code": self.code,
            "output_key": self.output_key
        }
        
        # Add input_args if present
        if self.input_args:
            script_dict["input_args"] = self.input_args
        
        return {"script": script_dict}


class HttpActionStep(ActionStep):
    """
    Specialized action step for HTTP requests.
    
    This extends ActionStep with HTTP-specific configuration options.
    """
    
    method: Optional[str] = Field(None, description="HTTP method (GET, POST, PUT, DELETE, etc.)")
    endpoint_url: Optional[str] = Field(None, description="HTTP endpoint URL")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    body: Optional[Dict[str, Any]] = Field(None, description="HTTP request body")
    
    @field_validator('method')
    @classmethod
    def validate_http_method(cls, v):
        """Validate HTTP method."""
        if v is not None:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
            if v.upper() not in valid_methods:
                raise ValueError(f"HTTP method must be one of: {', '.join(valid_methods)}")
            return v.upper()
        return v

    @field_validator('endpoint_url')
    @classmethod
    def validate_endpoint_url(cls, v):
        """Basic validation for endpoint URL."""
        if v is not None and not v.strip():
            raise ValueError("Endpoint URL cannot be empty if provided")
        return v
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this HTTP action step to YAML dictionary format."""
        # Start with base action dictionary
        result = super().to_yaml_dict()
        action_dict = result["action"]
        
        # Add HTTP-specific fields to input_args
        if not action_dict.get("input_args"):
            action_dict["input_args"] = {}
        
        if self.method:
            action_dict["input_args"]["method"] = self.method
        
        if self.endpoint_url:
            action_dict["input_args"]["endpoint_url"] = self.endpoint_url
        
        if self.headers:
            action_dict["input_args"]["headers"] = self.headers
        
        if self.body:
            action_dict["input_args"]["body"] = self.body
        
        return result
