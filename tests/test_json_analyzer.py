"""
Tests for JSON analysis functionality.

This module tests the JSON analyzer that helps users identify variables
from HTTP connector test results.
"""

import pytest
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.moveworks_wizard.utils.json_analyzer import (
    JSONAnalyzer, 
    VariableSuggestion, 
    analyze_json_string, 
    analyze_json_file
)


class TestJSONAnalyzer:
    """Test the JSONAnalyzer class."""
    
    def test_simple_json_analysis(self):
        """Test analysis of simple JSON structure."""
        json_data = {
            "id": 12345,
            "name": "John Doe",
            "email": "john.doe@company.com",
            "status": "active"
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "user_api")
        
        assert len(suggestions) == 4
        
        # Check that all fields are detected
        paths = [s.path for s in suggestions]
        assert "id" in paths
        assert "name" in paths
        assert "email" in paths
        assert "status" in paths
        
        # Check data types
        id_suggestion = next(s for s in suggestions if s.path == "id")
        assert id_suggestion.data_type == "integer"
        
        email_suggestion = next(s for s in suggestions if s.path == "email")
        assert email_suggestion.data_type == "email"
    
    def test_nested_json_analysis(self):
        """Test analysis of nested JSON structure."""
        json_data = {
            "user": {
                "id": 12345,
                "profile": {
                    "name": "John Doe",
                    "email": "john.doe@company.com"
                }
            },
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "source": "api"
            }
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "user_response")
        
        # Check nested paths
        paths = [s.path for s in suggestions]
        assert "user.id" in paths
        assert "user.profile.name" in paths
        assert "user.profile.email" in paths
        assert "metadata.created" in paths
        assert "metadata.source" in paths
        
        # Check bender expressions
        user_id_suggestion = next(s for s in suggestions if s.path == "user.id")
        assert user_id_suggestion.bender_expression == "user_response.user.id"
    
    def test_array_json_analysis(self):
        """Test analysis of JSON with arrays."""
        json_data = {
            "users": [
                {"id": 1, "name": "John"},
                {"id": 2, "name": "Jane"}
            ],
            "total": 2
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "users_api")
        
        paths = [s.path for s in suggestions]
        assert "users[0].id" in paths
        assert "users[0].name" in paths
        assert "users.length" in paths
        assert "total" in paths
    
    def test_data_type_detection(self):
        """Test detection of various data types."""
        json_data = {
            "string_field": "hello",
            "integer_field": 42,
            "float_field": 3.14,
            "boolean_field": True,
            "null_field": None,
            "email_field": "test@example.com",
            "url_field": "https://example.com",
            "uuid_field": "550e8400-e29b-41d4-a716-446655440000",
            "date_field": "2024-01-01T00:00:00Z",
            "array_field": [1, 2, 3],
            "object_field": {"key": "value"}
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test_data")
        
        # Create a mapping of path to data type
        type_map = {s.path: s.data_type for s in suggestions}
        
        assert type_map["string_field"] == "string"
        assert type_map["integer_field"] == "integer"
        assert type_map["float_field"] == "number"
        assert type_map["boolean_field"] == "boolean"
        assert type_map["null_field"] == "null"
        assert type_map["email_field"] == "email"
        assert type_map["url_field"] == "url"
        assert type_map["uuid_field"] == "uuid"
        assert type_map["date_field"] == "date"
        assert type_map["array_field"] == "array[3]"
        assert type_map["object_field"] == "object[1 keys]"
    
    def test_suggestion_priority(self):
        """Test that suggestions are prioritized correctly."""
        json_data = {
            "deeply": {
                "nested": {
                    "field": "value"
                }
            },
            "id": 123,
            "email": "test@example.com",
            "random_field": "data"
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test")
        
        # Common patterns (id, email) should be prioritized
        first_few_paths = [s.path for s in suggestions[:3]]
        assert "id" in first_few_paths
        assert "email" in first_few_paths
        
        # Deeply nested fields should be lower priority
        deeply_nested = next(s for s in suggestions if s.path == "deeply.nested.field")
        assert suggestions.index(deeply_nested) > 2
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        analyzer = JSONAnalyzer()
        
        with pytest.raises(ValueError, match="Invalid JSON data"):
            analyzer.analyze_json("invalid json", "test")
    
    def test_empty_json(self):
        """Test handling of empty JSON."""
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json("{}", "empty")
        
        assert len(suggestions) == 0
    
    def test_format_suggestions_for_display(self):
        """Test formatting suggestions for CLI display."""
        json_data = {"id": 123, "name": "test"}
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test")
        
        display_text = analyzer.format_suggestions_for_display(suggestions)
        
        assert "Variable Suggestions from JSON Analysis" in display_text
        assert "id" in display_text
        assert "name" in display_text
        assert "test.id" in display_text
        assert "test.name" in display_text
    
    def test_get_suggestions_by_type(self):
        """Test filtering suggestions by data type."""
        json_data = {
            "id": 123,
            "name": "test",
            "email": "test@example.com",
            "active": True
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test")
        
        string_suggestions = analyzer.get_suggestions_by_type("string")
        email_suggestions = analyzer.get_suggestions_by_type("email")
        boolean_suggestions = analyzer.get_suggestions_by_type("boolean")
        
        assert len(string_suggestions) == 1
        assert string_suggestions[0].path == "name"
        
        assert len(email_suggestions) == 1
        assert email_suggestions[0].path == "email"
        
        assert len(boolean_suggestions) == 1
        assert boolean_suggestions[0].path == "active"
    
    def test_get_suggestions_by_pattern(self):
        """Test filtering suggestions by pattern."""
        json_data = {
            "user_id": 123,
            "user_name": "test",
            "user_email": "test@example.com",
            "system_status": "active"
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test")
        
        user_suggestions = analyzer.get_suggestions_by_pattern("user")
        
        assert len(user_suggestions) == 3
        user_paths = [s.path for s in user_suggestions]
        assert "user_id" in user_paths
        assert "user_name" in user_paths
        assert "user_email" in user_paths
    
    def test_export_suggestions_to_json(self):
        """Test exporting suggestions to JSON file."""
        json_data = {"id": 123, "name": "test"}
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "test")
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            analyzer.export_suggestions_to_json(output_path)
            
            # Read back and verify
            with open(output_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            assert len(exported_data) == 2
            assert exported_data[0]["path"] in ["id", "name"]
            assert "bender_expression" in exported_data[0]
            assert "example_usage" in exported_data[0]
            
        finally:
            output_path.unlink()


class TestConvenienceFunctions:
    """Test convenience functions for JSON analysis."""
    
    def test_analyze_json_string(self):
        """Test analyze_json_string convenience function."""
        json_data = '{"id": 123, "name": "test"}'
        
        suggestions = analyze_json_string(json_data, "test_source")
        
        assert len(suggestions) == 2
        assert suggestions[0].bender_expression.startswith("test_source.")
    
    def test_analyze_json_file(self):
        """Test analyze_json_file convenience function."""
        json_data = {"id": 123, "name": "test"}
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            file_path = Path(f.name)
        
        try:
            suggestions = analyze_json_file(file_path, "file_source")
            
            assert len(suggestions) == 2
            assert suggestions[0].bender_expression.startswith("file_source.")
            
        finally:
            file_path.unlink()


class TestRealWorldExamples:
    """Test with real-world JSON examples."""
    
    def test_user_api_response(self):
        """Test with typical user API response."""
        json_data = {
            "data": {
                "user": {
                    "id": "usr_12345",
                    "email": "john.doe@company.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "department": "Engineering",
                    "manager": {
                        "id": "usr_67890",
                        "email": "manager@company.com"
                    },
                    "created_at": "2024-01-01T00:00:00Z",
                    "status": "active"
                }
            },
            "meta": {
                "request_id": "req_abc123",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "user_api_response")
        
        # Should find useful variables
        paths = [s.path for s in suggestions]
        assert "data.user.id" in paths
        assert "data.user.email" in paths
        assert "data.user.manager.id" in paths
        
        # Check example usage generation
        user_id_suggestion = next(s for s in suggestions if s.path == "data.user.id")
        assert "user_id" in user_id_suggestion.example_usage
    
    def test_ticket_api_response(self):
        """Test with typical ticket API response."""
        json_data = {
            "ticket": {
                "id": "TKT-12345",
                "title": "System Issue",
                "description": "The system is not working properly",
                "status": "open",
                "priority": "high",
                "assignee": {
                    "id": "usr_123",
                    "name": "Support Agent"
                },
                "created_by": {
                    "id": "usr_456",
                    "email": "user@company.com"
                },
                "tags": ["system", "urgent"],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(json_data), "ticket_response")
        
        # Should prioritize useful fields
        high_priority_paths = [s.path for s in suggestions[:5]]
        assert "ticket.id" in high_priority_paths
        assert "ticket.status" in high_priority_paths
        
        # Check that array handling works
        paths = [s.path for s in suggestions]
        assert "ticket.tags[0]" in paths
        assert "ticket.tags.length" in paths
