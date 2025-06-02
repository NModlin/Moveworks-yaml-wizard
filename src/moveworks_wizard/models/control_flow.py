"""
Models for control flow constructs in Compound Actions.

This includes switch statements, for loops, parallel execution, and try/catch blocks.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import Field, field_validator, model_validator

from .base import BaseStep


class SwitchCase(BaseStep):
    """
    Represents a single case in a switch statement.
    """
    
    condition: str = Field(..., description="Boolean condition using Bender syntax")
    steps: List[BaseStep] = Field(..., description="Steps to execute if condition is true")
    
    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v):
        """Validate the condition expression."""
        if not v.strip():
            raise ValueError("Switch case condition cannot be empty")
        return v.strip()
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "switch_case"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this switch case to YAML dictionary format."""
        return {
            "condition": self.condition,
            "steps": [step.to_yaml_dict() for step in self.steps]
        }


class SwitchStep(BaseStep):
    """
    Represents a switch/case control flow construct.
    
    Functions like an if/else or switch/case statement, allowing for
    multiple conditions to be evaluated with corresponding actions.
    """
    
    cases: List[SwitchCase] = Field(..., description="List of condition/steps pairs")
    default: Optional[List[BaseStep]] = Field(
        None,
        description="Default steps to execute if no conditions match"
    )
    
    @field_validator('cases')
    @classmethod
    def validate_cases(cls, v):
        """Ensure at least one case is provided."""
        if not v:
            raise ValueError("Switch statement must have at least one case")
        return v
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "switch"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this switch step to YAML dictionary format."""
        switch_dict = {
            "cases": [case.to_yaml_dict() for case in self.cases]
        }
        
        if self.default:
            switch_dict["default"] = {
                "steps": [step.to_yaml_dict() for step in self.default]
            }
        
        return {"switch": switch_dict}


class ForStep(BaseStep):
    """
    Represents a for/foreach loop construct.
    
    Allows iteration through each element of an iterable, executing
    a set of steps for each item.
    """
    
    each: str = Field(..., description="Variable name for the current item")
    index: str = Field(..., description="Variable name for the current index")
    in_variable: str = Field(..., alias="in", description="Name of the iterable variable")
    output_key: str = Field(..., description="Variable to store loop results")
    steps: List[BaseStep] = Field(..., description="Steps to execute for each item")
    
    @field_validator('each', 'index', 'in_variable', 'output_key')
    @classmethod
    def validate_variable_names(cls, v):
        """Validate variable names."""
        import re

        if not v.strip():
            raise ValueError("Variable names cannot be empty")

        # Variable names should be valid - must start with letter and contain only letters, numbers, underscores, hyphens
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v.strip()):
            raise ValueError("Variable names must start with a letter and contain only letters, numbers, underscores, and hyphens")

        return v.strip()
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "for"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this for step to YAML dictionary format."""
        return {
            "for": {
                "each": self.each,
                "index": self.index,
                "in": self.in_variable,
                "output_key": self.output_key,
                "steps": [step.to_yaml_dict() for step in self.steps]
            }
        }


class ParallelBranch(BaseStep):
    """
    Represents a single branch in parallel execution.
    """
    
    steps: List[BaseStep] = Field(..., description="Steps to execute in this branch")
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "parallel_branch"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this parallel branch to YAML dictionary format."""
        return {
            "steps": [step.to_yaml_dict() for step in self.steps]
        }


class ParallelStep(BaseStep):
    """
    Represents parallel execution of multiple expressions.
    
    Enables concurrent execution of independent tasks to optimize
    compound action performance.
    """
    
    # Option 1: Parallel branches
    branches: Optional[List[ParallelBranch]] = Field(
        None,
        description="List of branches to execute in parallel"
    )
    
    # Option 2: Parallel for loop
    for_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration for parallel for loop"
    )
    
    @model_validator(mode='after')
    def validate_parallel_config(self):
        """Ensure either branches or for_config is provided, but not both."""
        if self.branches is not None and self.for_config is not None:
            raise ValueError("Cannot specify both 'branches' and 'for_config'")

        if self.branches is None and self.for_config is None:
            raise ValueError("Must specify either 'branches' or 'for_config'")

        return self
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "parallel"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this parallel step to YAML dictionary format."""
        parallel_dict = {}
        
        if self.branches:
            parallel_dict["branches"] = [branch.to_yaml_dict() for branch in self.branches]
        elif self.for_config:
            parallel_dict["for"] = self.for_config
        
        return {"parallel": parallel_dict}


class TryCatchStep(BaseStep):
    """
    Represents a try/catch error handling construct.
    
    Allows execution of expressions with graceful error handling
    and recovery mechanisms.
    """
    
    try_steps: List[BaseStep] = Field(..., description="Steps to attempt execution")
    catch_steps: List[BaseStep] = Field(..., description="Steps to execute on error")
    on_status_code: Optional[List[Union[str, int]]] = Field(
        None,
        description="Specific status codes that trigger the catch block"
    )
    
    def get_step_type(self) -> str:
        """Return the step type identifier."""
        return "try_catch"
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert this try/catch step to YAML dictionary format."""
        try_catch_dict = {
            "try": {
                "steps": [step.to_yaml_dict() for step in self.try_steps]
            },
            "catch": {
                "steps": [step.to_yaml_dict() for step in self.catch_steps]
            }
        }
        
        if self.on_status_code:
            try_catch_dict["catch"]["on_status_code"] = self.on_status_code
        
        return {"try_catch": try_catch_dict}
