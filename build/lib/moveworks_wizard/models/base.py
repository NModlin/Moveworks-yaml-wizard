"""
Base models for Moveworks Compound Action YAML constructs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class BaseStep(BaseModel, ABC):
    """
    Abstract base class for all Compound Action steps.
    
    Each step type (action, script, switch, etc.) inherits from this base
    and implements the to_yaml_dict method to serialize to YAML structure.
    """
    
    @abstractmethod
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this step to a dictionary suitable for YAML serialization."""
        pass
    
    @abstractmethod
    def get_step_type(self) -> str:
        """Return the step type identifier (e.g., 'action', 'script', 'switch')."""
        pass


class CompoundAction(BaseModel):
    """
    Root model representing a complete Moveworks Compound Action.
    
    This is the top-level container that holds all the components of a 
    Compound Action YAML file, including input arguments and steps.
    """
    
    # Optional metadata (not part of YAML output but useful for wizard)
    name: Optional[str] = Field(None, description="Human-readable name for this compound action")
    description: Optional[str] = Field(None, description="Description of what this compound action does")
    
    # Core Compound Action components
    input_args: Optional[Dict[str, Any]] = Field(
        None, 
        description="Input arguments for the compound action using Bender syntax"
    )
    
    # Steps can be either a single step or a list of steps
    steps: Optional[List[BaseStep]] = Field(
        None,
        description="List of steps to execute in the compound action"
    )
    
    # For single-step compound actions, we can have a direct step
    single_step: Optional[BaseStep] = Field(
        None,
        description="Single step for simple compound actions (alternative to steps list)"
    )
    
    @model_validator(mode='after')
    def validate_steps_configuration(self):
        """Ensure either steps or single_step is provided, but not both."""
        if self.steps is not None and self.single_step is not None:
            raise ValueError("Cannot specify both 'steps' and 'single_step'")

        if self.steps is None and self.single_step is None:
            raise ValueError("Must specify either 'steps' or 'single_step'")

        return self
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """
        Convert this CompoundAction to a dictionary suitable for YAML serialization.

        Returns:
            Dictionary representing the complete Compound Action YAML structure
        """
        result = {}

        # Handle single step vs multiple steps FIRST (correct Moveworks order)
        if self.single_step:
            # For single step, add it directly to the root level
            step_dict = self.single_step.to_yaml_dict()
            result.update(step_dict)
        elif self.steps:
            # For multiple steps, wrap in steps array
            result['steps'] = [step.to_yaml_dict() for step in self.steps]

        # Add input_args AFTER steps if present
        if self.input_args:
            result['input_args'] = self.input_args

        return result
    
    def add_step(self, step: BaseStep) -> None:
        """
        Add a step to this compound action.
        
        Args:
            step: The step to add
        """
        if self.single_step is not None:
            # Convert single step to steps list
            self.steps = [self.single_step, step]
            self.single_step = None
        elif self.steps is None:
            self.steps = [step]
        else:
            self.steps.append(step)
    
    def get_step_count(self) -> int:
        """Return the total number of steps in this compound action."""
        if self.single_step:
            return 1
        elif self.steps:
            return len(self.steps)
        else:
            return 0
