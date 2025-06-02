#!/usr/bin/env python3
"""
Test script for the GUI functionality.

This script tests the main GUI features including JSON analysis.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_import():
    """Test that the GUI can be imported."""
    try:
        from moveworks_wizard.gui.main_window import MoveworksWizardGUI
        print("✅ GUI imports successfully")
        return True
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        return False

def test_json_analyzer_import():
    """Test that the JSON analyzer can be imported."""
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        print("✅ JSON analyzer imports successfully")
        return True
    except Exception as e:
        print(f"❌ JSON analyzer import failed: {e}")
        return False

def test_json_analysis():
    """Test JSON analysis functionality."""
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        # Test with sample data
        sample_json = '''
        {
            "data": {
                "user": {
                    "id": "usr_123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
            },
            "success": true
        }
        '''
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(sample_json, "test_api")
        
        if suggestions:
            print(f"✅ JSON analysis works - found {len(suggestions)} suggestions")
            for suggestion in suggestions[:3]:
                print(f"   • {suggestion.path} ({suggestion.data_type})")
            return True
        else:
            print("❌ JSON analysis returned no suggestions")
            return False
            
    except Exception as e:
        print(f"❌ JSON analysis failed: {e}")
        return False

def test_gui_creation():
    """Test that the GUI can be created (but not shown)."""
    try:
        from moveworks_wizard.gui.main_window import MoveworksWizardGUI
        
        # Create GUI instance but don't run it
        app = MoveworksWizardGUI()
        
        # Test that basic components exist
        assert hasattr(app, 'root')
        assert hasattr(app, 'compound_action')
        assert hasattr(app, 'input_args_tree')
        assert hasattr(app, 'steps_tree')
        
        print("✅ GUI creation successful")
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Moveworks YAML Wizard GUI")
    print("=" * 50)
    
    tests = [
        test_gui_import,
        test_json_analyzer_import,
        test_json_analysis,
        test_gui_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The GUI is ready to use.")
        print("\nTo run the GUI:")
        print("  python -m src.moveworks_wizard.gui.main_window")
        print("\nOr use the CLI:")
        print("  python -m src.moveworks_wizard.wizard.cli wizard")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
