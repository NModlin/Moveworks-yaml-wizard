#!/usr/bin/env python3
"""
Complete test of the JSON selection workflow.
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_json_file():
    """Create a comprehensive test JSON file."""
    test_data = {
        "data": {
            "user": {
                "id": "usr_12345",
                "email": "john.doe@company.com",
                "name": "John Doe",
                "department": "Engineering",
                "role": "Senior Developer",
                "active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "metadata": {
                    "last_login": "2024-01-20T14:22:00Z",
                    "login_count": 42,
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            },
            "organization": {
                "id": "org_67890",
                "name": "Tech Corp",
                "domain": "techcorp.com",
                "plan": "enterprise",
                "settings": {
                    "sso_enabled": True,
                    "max_users": 1000
                }
            },
            "permissions": [
                "read:users",
                "write:users",
                "admin:org"
            ]
        },
        "success": True,
        "message": "User data retrieved successfully",
        "timestamp": "2024-01-20T15:45:30Z",
        "request_id": "req_abc123def456"
    }
    
    # Ensure examples directory exists
    os.makedirs('examples', exist_ok=True)
    
    # Write the test file
    with open('examples/comprehensive_test.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    return test_data

def test_json_analysis():
    """Test the JSON analysis functionality."""
    print("🔍 Testing JSON Analysis")
    print("-" * 30)
    
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        # Create test data
        test_data = create_test_json_file()
        print("✅ Created comprehensive test JSON file")
        
        # Analyze the JSON
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(test_data), "user_api")
        
        print(f"✅ Generated {len(suggestions)} variable suggestions")
        
        # Show top suggestions
        print("\n📋 Top 10 Variable Suggestions:")
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"{i:2d}. {suggestion.path}")
            print(f"    Type: {suggestion.data_type}")
            print(f"    Bender: {suggestion.bender_expression}")
            print()
        
        return suggestions
        
    except Exception as e:
        print(f"❌ JSON analysis failed: {e}")
        return None

def test_argument_generation(suggestions):
    """Test the argument name generation logic."""
    print("🏷️  Testing Argument Name Generation")
    print("-" * 40)
    
    if not suggestions:
        print("❌ No suggestions to test")
        return False
    
    try:
        # Simulate the argument generation process
        input_args = {}
        
        for suggestion in suggestions[:8]:  # Test with first 8
            # Generate argument name (same logic as in GUI)
            path_parts = suggestion.path.split('.')
            if len(path_parts) > 1:
                arg_name = '_'.join(path_parts[-2:]).lower()
            else:
                arg_name = path_parts[-1].lower()
            
            # Ensure unique names
            original_name = arg_name
            counter = 1
            while arg_name in input_args:
                arg_name = f"{original_name}_{counter}"
                counter += 1
            
            input_args[arg_name] = suggestion.bender_expression
            print(f"✅ {suggestion.path} → {arg_name}")
        
        print(f"\n📊 Generated {len(input_args)} unique argument names")
        return True
        
    except Exception as e:
        print(f"❌ Argument generation failed: {e}")
        return False

def test_selection_patterns():
    """Test the selection pattern logic."""
    print("🎯 Testing Selection Patterns")
    print("-" * 30)
    
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        # Test with sample data
        test_json = '''
        {
            "user_id": "123",
            "user_email": "test@example.com", 
            "user_name": "Test User",
            "status": "active",
            "data": {"value": 42},
            "metadata": {"info": "test"},
            "random_field": "xyz"
        }
        '''
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(test_json, "test_api")
        
        # Test common pattern matching
        common_patterns = ['id', 'email', 'name', 'status', 'user', 'data']
        common_matches = []
        
        for suggestion in suggestions:
            path = suggestion.path.lower()
            if any(pattern in path for pattern in common_patterns):
                common_matches.append(suggestion.path)
        
        print(f"✅ Found {len(common_matches)} common pattern matches:")
        for match in common_matches:
            print(f"   - {match}")
        
        return True
        
    except Exception as e:
        print(f"❌ Selection pattern test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Complete JSON Selection Workflow Test")
    print("=" * 50)
    
    # Test 1: JSON Analysis
    suggestions = test_json_analysis()
    
    # Test 2: Argument Generation
    if suggestions:
        test_argument_generation(suggestions)
    
    # Test 3: Selection Patterns
    test_selection_patterns()
    
    print("\n" + "=" * 50)
    print("🎯 Manual Testing Instructions")
    print("=" * 50)
    
    print("\n1. 🚀 Launch the GUI:")
    print("   python -m src.moveworks_wizard.gui.main_window")
    
    print("\n2. 📝 Create New Compound Action:")
    print("   - Click 'New Compound Action'")
    print("   - Enter name: 'Test User API'")
    print("   - Enter description: 'Test JSON selection'")
    
    print("\n3. 🔍 Test JSON Analysis:")
    print("   - Click 'Analyze JSON' in Quick Start")
    print("   - Click 'Load from File'")
    print("   - Select 'examples/comprehensive_test.json'")
    print("   - Click 'Analyze'")
    
    print("\n4. ✅ Verify Dialog Layout:")
    print("   - Dialog opens at 900x700 size")
    print("   - Instructions at top")
    print("   - Tree view with variables in middle")
    print("   - Quick Selection buttons below tree")
    print("   - 'Add Selected (0)' button at bottom right")
    print("   - 'Cancel' button at bottom right")
    print("   - Selection counter at bottom left")
    
    print("\n5. 🎯 Test Selection:")
    print("   - Click individual variables to select")
    print("   - Hold Ctrl and click for multiple selection")
    print("   - Try 'Select Top 5' button")
    print("   - Try 'Select Common' button")
    print("   - Watch counter update: '5 items selected'")
    print("   - Watch button update: 'Add Selected (5)'")
    
    print("\n6. ➕ Add Variables:")
    print("   - Click 'Add Selected (X)' button")
    print("   - Variables should appear in Input Arguments")
    print("   - Check argument names are meaningful")
    print("   - Verify Bender expressions are correct")
    
    print("\n7. 🔄 Test Multiple Rounds:")
    print("   - Click 'Analyze JSON' again")
    print("   - Select different variables")
    print("   - Add them (should not duplicate)")
    print("   - Verify unique argument names")
    
    print("\n🎉 Expected Results:")
    print("✅ All buttons visible and functional")
    print("✅ Selection works with visual feedback")
    print("✅ Variables added with good names")
    print("✅ No duplicates or conflicts")
    print("✅ Professional user experience")
    
    print(f"\n📁 Test file created: examples/comprehensive_test.json")
    print("   Use this file for comprehensive testing!")

if __name__ == "__main__":
    main()
