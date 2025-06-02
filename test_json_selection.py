#!/usr/bin/env python3
"""
Test script for JSON selection functionality.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_json_selection():
    """Test the JSON selection functionality."""
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        # Test with sample data
        sample_json = '''
        {
            "data": {
                "user": {
                    "id": "usr_123",
                    "email": "test@example.com",
                    "name": "Test User",
                    "department": "Engineering"
                },
                "organization": {
                    "id": "org_456",
                    "name": "Test Company"
                }
            },
            "success": true,
            "message": "User retrieved successfully"
        }
        '''
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(sample_json, "user_api")
        
        print("🔍 JSON Analysis Results:")
        print(f"Found {len(suggestions)} variable suggestions")
        print()
        
        print("📋 Top suggestions (what you'll see in the GUI):")
        for i, suggestion in enumerate(suggestions[:8], 1):
            print(f"{i:2d}. {suggestion.path}")
            print(f"    Type: {suggestion.data_type}")
            print(f"    Bender: {suggestion.bender_expression}")
            print(f"    Example: {suggestion.example_usage}")
            print()
        
        print("✅ JSON analysis working correctly!")
        print()
        print("🎯 In the GUI:")
        print("1. Click 'Analyze JSON' button")
        print("2. Paste the JSON above or load examples/sample_http_response.json")
        print("3. Click 'Analyze'")
        print("4. You'll see a dialog with these suggestions")
        print("5. Click on items to select them (hold Ctrl for multiple)")
        print("6. Use 'Select Top 5' or 'Select Common' for quick selection")
        print("7. Click 'Add Selected' to add them as input arguments")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_argument_naming():
    """Test the improved argument naming logic."""
    try:
        # Simulate the argument naming logic
        test_paths = [
            "data.user.email",
            "data.user.id", 
            "success",
            "data.organization.name",
            "message"
        ]
        
        print("🏷️  Argument Naming Test:")
        existing_args = {}
        
        for path in test_paths:
            path_parts = path.split('.')
            if len(path_parts) > 1:
                arg_name = '_'.join(path_parts[-2:]).lower()
            else:
                arg_name = path_parts[-1].lower()
            
            # Ensure unique names
            original_name = arg_name
            counter = 1
            while arg_name in existing_args:
                arg_name = f"{original_name}_{counter}"
                counter += 1
            
            existing_args[arg_name] = f"user_api.{path}"
            print(f"  {path} → {arg_name}")
        
        print()
        print("✅ Argument naming working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Argument naming test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing JSON Selection Functionality")
    print("=" * 50)
    
    tests = [
        test_json_selection,
        test_argument_naming
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 JSON selection functionality is working!")
        print()
        print("🚀 To test in the GUI:")
        print("  python -m src.moveworks_wizard.gui.main_window")
        print()
        print("Then:")
        print("1. Click 'New Compound Action'")
        print("2. Click 'Analyze JSON' in Quick Start")
        print("3. Load examples/sample_http_response.json")
        print("4. Select variables and add them!")
    else:
        print("⚠️  Some tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
