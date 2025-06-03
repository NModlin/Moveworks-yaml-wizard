"""
JSON Analysis Utility for HTTP Connector Test Results

This module provides functionality to analyze JSON responses from HTTP connectors
and suggest variable paths that can be used in Compound Actions.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VariableSuggestion:
    """Represents a suggested variable path from JSON analysis."""
    path: str
    value: Any
    data_type: str
    description: str
    bender_expression: str
    example_usage: str


class JSONAnalyzer:
    """
    Analyzes JSON responses from HTTP connectors to suggest variable paths
    for use in Compound Action input arguments and step parameters.
    """
    
    def __init__(self):
        self.suggestions: List[VariableSuggestion] = []
        self.common_patterns = {
            'id': 'Unique identifier',
            'email': 'Email address',
            'name': 'Display name',
            'status': 'Status indicator',
            'created': 'Creation timestamp',
            'updated': 'Last update timestamp',
            'url': 'URL or endpoint',
            'token': 'Authentication token',
            'user': 'User information',
            'data': 'Data payload',
            'result': 'Operation result',
            'error': 'Error information',
            'message': 'Message content',
            'code': 'Status or error code',
            'success': 'Success indicator'
        }
    
    def analyze_json(self, json_data: str, source_name: str = "http_response") -> List[VariableSuggestion]:
        """
        Analyze JSON data and return variable suggestions.
        
        Args:
            json_data: JSON string from HTTP connector test results
            source_name: Name of the source (e.g., "user_api_response")
            
        Returns:
            List of VariableSuggestion objects
        """
        try:
            parsed_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        
        self.suggestions = []
        self._analyze_object(parsed_data, source_name, "")

        # Remove duplicates and sort suggestions by usefulness
        self._remove_duplicate_suggestions()
        self.suggestions.sort(key=self._suggestion_priority)

        return self.suggestions
    
    def _analyze_object(self, obj: Any, source_name: str, current_path: str) -> None:
        """Recursively analyze JSON object and extract variable paths."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                self._add_suggestion(new_path, value, source_name)

                # Recursively analyze nested objects (limit depth to avoid excessive suggestions)
                if isinstance(value, (dict, list)) and len(current_path.split('.')) < 4:
                    self._analyze_object(value, source_name, new_path)

        elif isinstance(obj, list) and obj:
            # Comprehensive array analysis
            self._analyze_array_comprehensive(obj, source_name, current_path)

    def _analyze_array_comprehensive(self, array: List[Any], source_name: str, current_path: str) -> None:
        """
        Comprehensively analyze an array to discover all properties across all items.
        This provides better suggestions for array iteration and property extraction.
        """
        if not array:
            return

        # Add basic array suggestions
        if current_path:
            # Array itself for iteration
            self._add_suggestion(current_path, array, source_name)

            # Array length
            length_path = f"{current_path}.length"
            self._add_suggestion(length_path, len(array), source_name, is_computed=True)

        # Analyze first item as example (existing behavior)
        array_path = f"{current_path}[0]" if current_path else "[0]"
        self._add_suggestion(array_path, array[0], source_name)

        # If array contains objects, discover all unique properties across all items
        if isinstance(array[0], dict):
            self._analyze_array_objects_comprehensive(array, source_name, current_path)

        # Recursively analyze the first item if it's complex (existing behavior)
        # But avoid duplicate analysis that _analyze_array_objects_comprehensive already does
        if isinstance(array[0], (dict, list)) and len(current_path.split('.')) < 4:
            if not isinstance(array[0], dict):  # Only if not already handled above
                self._analyze_object(array[0], source_name, array_path)

    def _analyze_array_objects_comprehensive(self, array: List[dict], source_name: str, current_path: str) -> None:
        """
        Analyze an array of objects to discover all unique properties and generate
        comprehensive suggestions for array iteration and data extraction.
        """
        # Collect all unique properties across all objects in the array
        all_properties = set()
        property_examples = {}
        property_types = {}

        for item in array:
            if isinstance(item, dict):
                for key, value in item.items():
                    all_properties.add(key)
                    if key not in property_examples:
                        property_examples[key] = value
                        property_types[key] = self._get_data_type(value)

        # Generate suggestions for each unique property found across all array items
        for prop in sorted(all_properties):
            example_value = property_examples[prop]
            data_type = property_types[prop]

            # Individual property access pattern - use valid bender syntax
            if current_path:
                # For nested arrays, suggest iteration pattern
                prop_path = f"{current_path}[*].{prop}"
                bender_expr = f"ARRAY({source_name}.{current_path}, item.{prop})"
            else:
                # For root arrays
                prop_path = f"[*].{prop}"
                bender_expr = f"ARRAY({source_name}, item.{prop})"

            # Create a special suggestion for array property extraction
            suggestion = VariableSuggestion(
                path=prop_path,
                value=example_value,
                data_type=f"array_property[{data_type}]",
                description=f"All {prop} values from array items ({data_type})",
                bender_expression=bender_expr,
                example_usage=self._generate_array_property_usage(prop, data_type, current_path, source_name)
            )
            self.suggestions.append(suggestion)

            # Also add nested analysis for complex properties
            if isinstance(example_value, (dict, list)) and len(current_path.split('.')) < 3:
                nested_path = f"{current_path}[0].{prop}" if current_path else f"[0].{prop}"
                self._analyze_object(example_value, source_name, nested_path)

    def _generate_array_property_usage(self, property_name: str, data_type: str, array_path: str, source_name: str) -> str:
        """Generate example usage for extracting a property from all items in an array."""
        if array_path:
            full_path = f"{source_name}.{array_path}"
        else:
            full_path = source_name

        # Generate YAML-like usage examples for array property extraction
        if "id" in property_name.lower():
            return f"""steps:
  - for_each: "{full_path}"
    output_key: "all_{property_name}s"
    script:
      code: "return [item.{property_name} for item in {full_path}]" """
        elif "name" in property_name.lower():
            return f"""steps:
  - for_each: "{full_path}"
    output_key: "{property_name}_list"
    script:
      code: "return [item.{property_name} for item in {full_path}]" """
        else:
            return f"""steps:
  - for_each: "{full_path}"
    output_key: "{property_name}_values"
    script:
      code: "return [item.{property_name} for item in {full_path}]" """

    def _add_suggestion(self, path: str, value: Any, source_name: str, is_computed: bool = False) -> None:
        """Add a variable suggestion based on the path and value."""
        data_type = self._get_data_type(value)
        description = self._generate_description(path, value, data_type)
        bender_expression = f"{source_name}.{path}"
        example_usage = self._generate_example_usage(path, value, data_type)
        
        suggestion = VariableSuggestion(
            path=path,
            value=value,
            data_type=data_type,
            description=description,
            bender_expression=bender_expression,
            example_usage=example_usage
        )
        
        self.suggestions.append(suggestion)
    
    def _get_data_type(self, value: Any) -> str:
        """Determine the data type of a value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            # Check for special string patterns
            if re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
                return "date"
            elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(value)):
                return "email"
            elif re.match(r'^https?://', str(value)):
                return "url"
            elif re.match(r'^[0-9a-fA-F-]{36}$', str(value)):
                return "uuid"
            else:
                return "string"
        elif isinstance(value, list):
            return f"array[{len(value)}]"
        elif isinstance(value, dict):
            return f"object[{len(value)} keys]"
        else:
            return "unknown"
    
    def _generate_description(self, path: str, value: Any, data_type: str) -> str:
        """Generate a human-readable description for the variable."""
        # Check for common patterns in the path
        path_lower = path.lower()
        for pattern, desc in self.common_patterns.items():
            if pattern in path_lower:
                return f"{desc} ({data_type})"
        
        # Generate description based on data type and value
        if data_type == "string" and isinstance(value, str):
            if len(value) > 50:
                return f"Text content ({len(value)} characters)"
            else:
                return f"String value: '{value}'"
        elif data_type.startswith("array"):
            return f"Array with {len(value)} items"
        elif data_type.startswith("object"):
            return f"Object with {len(value)} properties"
        elif data_type in ["integer", "number"]:
            return f"Numeric value: {value}"
        elif data_type == "boolean":
            return f"Boolean flag: {value}"
        else:
            return f"Value of type {data_type}"
    
    def _generate_example_usage(self, path: str, value: Any, data_type: str) -> str:
        """Generate example usage for the variable in Compound Actions."""
        # Handle array property types specially
        if data_type.startswith("array_property"):
            property_name = path.split('.')[-1] if '.' in path else path.replace('[*].', '')
            return f"""# Extract all {property_name} values from array:
for_each: "{path.replace('[*]', '')}"
output_key: "all_{property_name}_values"
script:
  code: "return [item.{property_name} for item in data]" """

        # Standard property handling
        elif "id" in path.lower():
            return f"input_args: {{\"user_id\": \"{path}\"}}"
        elif "email" in path.lower():
            return f"input_args: {{\"recipient\": \"{path}\"}}"
        elif "name" in path.lower():
            return f"RENDER('Hello {{{{name}}}}', {{{path}}})"
        elif "status" in path.lower():
            return f"switch_on: \"{path}\""
        elif data_type == "boolean":
            return f"condition: \"{path} == true\""
        elif data_type.startswith("array"):
            return f"for_each: \"{path}\""
        else:
            return f"input_args: {{\"data\": \"{path}\"}}"
    
    def _suggestion_priority(self, suggestion: VariableSuggestion) -> Tuple[int, int, str]:
        """Calculate priority for sorting suggestions (lower = higher priority)."""
        # Prioritize array property suggestions (new comprehensive array handling)
        array_property_priority = 0
        if suggestion.data_type.startswith("array_property"):
            array_property_priority = -15  # Highest priority for array properties

        # Prioritize common patterns
        pattern_priority = 0
        path_lower = suggestion.path.lower()
        for pattern in self.common_patterns.keys():
            if pattern in path_lower:
                pattern_priority = -10
                break

        # Prioritize shorter paths
        depth_penalty = len(suggestion.path.split('.'))

        # Prioritize useful data types
        type_priority = 0
        if suggestion.data_type in ["string", "integer", "boolean"]:
            type_priority = -5
        elif suggestion.data_type in ["email", "uuid", "url"]:
            type_priority = -8
        elif suggestion.data_type.startswith("array"):
            type_priority = -6  # Arrays are useful for iteration

        return (array_property_priority + pattern_priority + type_priority, depth_penalty, suggestion.path)

    def _remove_duplicate_suggestions(self) -> None:
        """Remove duplicate suggestions based on path and bender expression."""
        seen = set()
        unique_suggestions = []

        for suggestion in self.suggestions:
            # Create a unique key based on path and bender expression
            key = (suggestion.path, suggestion.bender_expression)
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)

        self.suggestions = unique_suggestions

    def format_suggestions_for_display(self, suggestions: List[VariableSuggestion],
                                     max_suggestions: int = 20) -> str:
        """Format suggestions for CLI display."""
        if not suggestions:
            return "No variable suggestions found."
        
        output = ["📊 Variable Suggestions from JSON Analysis:", ""]
        
        for i, suggestion in enumerate(suggestions[:max_suggestions], 1):
            output.append(f"{i:2d}. {suggestion.path}")
            output.append(f"    Type: {suggestion.data_type}")
            output.append(f"    Description: {suggestion.description}")
            output.append(f"    Bender: {suggestion.bender_expression}")
            output.append(f"    Example: {suggestion.example_usage}")
            output.append("")
        
        if len(suggestions) > max_suggestions:
            output.append(f"... and {len(suggestions) - max_suggestions} more suggestions")
        
        return "\n".join(output)
    
    def get_suggestions_by_type(self, data_type: str) -> List[VariableSuggestion]:
        """Get suggestions filtered by data type."""
        return [s for s in self.suggestions if s.data_type == data_type]
    
    def get_suggestions_by_pattern(self, pattern: str) -> List[VariableSuggestion]:
        """Get suggestions that match a specific pattern."""
        pattern_lower = pattern.lower()
        return [s for s in self.suggestions if pattern_lower in s.path.lower()]
    
    def export_suggestions_to_json(self, output_path: Path) -> None:
        """Export suggestions to a JSON file for later use."""
        suggestions_data = []
        for suggestion in self.suggestions:
            suggestions_data.append({
                "path": suggestion.path,
                "value": suggestion.value,
                "data_type": suggestion.data_type,
                "description": suggestion.description,
                "bender_expression": suggestion.bender_expression,
                "example_usage": suggestion.example_usage
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions_data, f, indent=2, ensure_ascii=False)

    def generate_comprehensive_yaml_example(self, source_name: str = "api_response") -> str:
        """
        Generate a comprehensive YAML example that extracts all array properties
        found in the JSON analysis. This creates a complete Moveworks Compound Action
        that processes all array data with valid YAML schema.
        """
        array_properties = [s for s in self.suggestions if s.data_type.startswith("array_property")]

        if not array_properties:
            return "# No array properties found to extract"

        yaml_lines = [
            "# Comprehensive data extraction from JSON arrays",
            "# This YAML extracts all properties from array items",
            "",
            "steps:"
        ]

        step_counter = 1
        valid_output_keys = []

        for suggestion in array_properties:
            property_name = suggestion.path.split('.')[-1].replace('[*]', '')
            array_path = suggestion.path.replace('[*].' + property_name, '').replace('[*]', '')

            # Create valid output key (no special characters, camelCase)
            clean_property_name = self._clean_property_name(property_name)
            output_key = f"extracted{clean_property_name.capitalize()}List"
            valid_output_keys.append((output_key, property_name))

            if array_path:
                full_array_path = f"{source_name}.{array_path}"
            else:
                full_array_path = source_name

            yaml_lines.extend([
                f"  - # Step {step_counter}: Extract all {property_name} values",
                f"    script:",
                f"      code: |",
                f"        # Extract {property_name} from all items in {array_path or 'root array'}",
                f"        result = []",
                f"        for item in {full_array_path}:",
                f"          if '{property_name}' in item:",
                f"            result.append(item['{property_name}'])",
                f"        return result",
                f"    output_key: {output_key}",
                ""
            ])
            step_counter += 1

        # Add a final step that combines all results
        yaml_lines.extend([
            f"  - # Step {step_counter}: Combine all extracted data",
            f"    script:",
            f"      code: |",
            f"        # Combine all extracted array properties into a summary",
            f"        summary = {{}}",
        ])

        for output_key, property_name in valid_output_keys:
            yaml_lines.append(f"        summary['{property_name}_list'] = {output_key}")

        yaml_lines.extend([
            f"        return summary",
            f"    output_key: extractedDataSummary",
            f"    input_args:",
        ])

        for output_key, _ in valid_output_keys:
            yaml_lines.append(f"      {output_key}: \"{output_key}\"")

        return "\n".join(yaml_lines)

    def _clean_property_name(self, property_name: str) -> str:
        """Clean property name to be valid for YAML keys."""
        # Remove special characters and convert to camelCase
        import re
        # Remove special characters
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', property_name)
        # Ensure it starts with a letter
        if clean_name and clean_name[0].isdigit():
            clean_name = 'prop' + clean_name
        return clean_name or 'property'


def analyze_json_file(file_path: Path, source_name: str = "http_response") -> List[VariableSuggestion]:
    """
    Convenience function to analyze JSON from a file.
    
    Args:
        file_path: Path to JSON file
        source_name: Name of the source for variable suggestions
        
    Returns:
        List of VariableSuggestion objects
    """
    analyzer = JSONAnalyzer()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()
    
    return analyzer.analyze_json(json_data, source_name)


def analyze_json_string(json_string: str, source_name: str = "http_response") -> List[VariableSuggestion]:
    """
    Convenience function to analyze JSON from a string.
    
    Args:
        json_string: JSON data as string
        source_name: Name of the source for variable suggestions
        
    Returns:
        List of VariableSuggestion objects
    """
    analyzer = JSONAnalyzer()
    return analyzer.analyze_json(json_string, source_name)
