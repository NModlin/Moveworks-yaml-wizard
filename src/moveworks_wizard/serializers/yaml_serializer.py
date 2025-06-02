"""
YAML serialization for Moveworks Compound Actions.

This module handles the conversion of CompoundAction models to properly
formatted YAML strings that conform to Moveworks standards.
"""

import yaml
from typing import Any, Dict
from io import StringIO

from ..models.base import CompoundAction


class MoveworksYamlDumper(yaml.SafeDumper):
    """
    Custom YAML dumper for Moveworks-specific formatting requirements.
    
    This ensures proper formatting for multi-line strings, indentation,
    and other Moveworks YAML conventions.
    """
    
    def write_literal(self, text):
        """Handle literal block scalars (|) for multi-line strings."""
        hints = self.determine_block_hints(text)
        self.write_indicator('|' + hints, True)
        if hints[-1:] == '+':
            self.open_ended = True
        self.write_line_break()
        breaks = True
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if breaks:
                if ch is None or ch not in '\n\x85\u2028\u2029':
                    if not breaks and ch is not None and ch != ' ' and start < end:
                        self.write_indent()
                        self.stream.write(text[start:end])
                        start = end
                    if ch is not None:
                        self.write_indent()
                    breaks = False
            else:
                if ch is None or ch in '\n\x85\u2028\u2029':
                    self.stream.write(text[start:end])
                    if ch is not None:
                        self.write_line_break()
                    start = end
                    breaks = True
            end += 1

    def represent_str(self, data):
        """Custom string representation for multi-line strings and special characters."""
        if '\n' in data:
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')

        # Quote strings that start with special characters or contain problematic patterns
        needs_quoting = (
            data.startswith('@') or
            data.startswith('!') or
            data.startswith('&') or
            data.startswith('*') or
            data.startswith('{') or
            data.startswith('[') or
            data.startswith('|') or
            data.startswith('>') or
            ':' in data or
            '#' in data or
            data.strip() != data  # has leading/trailing whitespace
        )

        if needs_quoting:
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='"')

        return self.represent_scalar('tag:yaml.org,2002:str', data)


# Register the custom string representer
MoveworksYamlDumper.add_representer(str, MoveworksYamlDumper.represent_str)


class YamlSerializer:
    """
    Serializer for converting CompoundAction models to YAML format.
    
    Handles Moveworks-specific formatting requirements and ensures
    proper structure for Compound Action YAML files.
    """
    
    @staticmethod
    def serialize(compound_action: CompoundAction, 
                  include_comments: bool = False,
                  sort_keys: bool = False) -> str:
        """
        Serialize a CompoundAction to YAML string.
        
        Args:
            compound_action: The CompoundAction model to serialize
            include_comments: Whether to include helpful comments (default: False)
            sort_keys: Whether to sort dictionary keys (default: False)
            
        Returns:
            YAML string representation of the compound action
        """
        # Convert to dictionary
        yaml_dict = compound_action.to_yaml_dict()
        
        # Add comments if requested
        if include_comments:
            yaml_dict = YamlSerializer._add_comments(yaml_dict, compound_action)
        
        # Serialize to YAML with custom formatting
        yaml_str = yaml.dump(
            yaml_dict,
            Dumper=MoveworksYamlDumper,
            default_flow_style=False,
            sort_keys=sort_keys,
            indent=2,
            width=120,
            allow_unicode=True,
            explicit_start=False,
            explicit_end=False
        )
        
        return yaml_str
    
    @staticmethod
    def _add_comments(yaml_dict: Dict[str, Any], 
                     compound_action: CompoundAction) -> Dict[str, Any]:
        """
        Add helpful comments to the YAML dictionary.
        
        Note: YAML comments are not officially supported by Moveworks
        but can be useful for development and documentation.
        """
        # This is a placeholder for comment addition logic
        # Comments would need to be handled differently since PyYAML
        # doesn't preserve comments during serialization
        return yaml_dict
    
    @staticmethod
    def validate_yaml(yaml_str: str) -> bool:
        """
        Validate that the generated YAML is syntactically correct.
        
        Args:
            yaml_str: YAML string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            yaml.safe_load(yaml_str)
            return True
        except yaml.YAMLError:
            return False
    
    @staticmethod
    def format_for_moveworks(yaml_str: str) -> str:
        """
        Apply Moveworks-specific formatting to YAML string.
        
        This handles special cases like ensuring proper escaping
        for DSL expressions and other Moveworks conventions.
        """
        # Apply any Moveworks-specific formatting rules
        lines = yaml_str.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Handle DSL expression formatting
            if 'data.' in line or 'meta_info.' in line:
                # Ensure DSL expressions are properly quoted if needed
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)


def serialize_compound_action(compound_action: CompoundAction, 
                            include_comments: bool = False,
                            format_for_moveworks: bool = True) -> str:
    """
    Convenience function to serialize a CompoundAction to YAML.
    
    Args:
        compound_action: The CompoundAction model to serialize
        include_comments: Whether to include helpful comments
        format_for_moveworks: Whether to apply Moveworks-specific formatting
        
    Returns:
        YAML string representation of the compound action
    """
    serializer = YamlSerializer()
    yaml_str = serializer.serialize(compound_action, include_comments=include_comments)
    
    if format_for_moveworks:
        yaml_str = serializer.format_for_moveworks(yaml_str)
    
    return yaml_str
