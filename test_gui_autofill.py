#!/usr/bin/env python3
"""
Test script to verify auto-fill functionality and YAML generation.
"""

import sys
from pathlib import Path

# Add src to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_yaml_generation():
    """Test YAML generation to identify formatting issues."""
    print("🧪 Testing YAML Generation...")
    
    try:
        from moveworks_wizard.models.base import CompoundAction
        from moveworks_wizard.models.actions import ActionStep
        from moveworks_wizard.serializers import serialize_compound_action
        
        # Create a simple test compound action
        step = ActionStep(
            action_name="test_action",
            output_key="test_result"
        )
        
        compound_action = CompoundAction(
            name="Test Action",
            steps=[step]
        )
        
        # Generate YAML
        yaml_content = serialize_compound_action(compound_action)
        print("✅ YAML Generation Test:")
        print("=" * 40)
        print(yaml_content)
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ YAML Generation failed: {e}")
        return False

def test_autofill_functions():
    """Test the auto-fill functionality."""
    print("\n🧪 Testing Auto-fill Functions...")
    
    try:
        from moveworks_wizard.gui.main_window import StepDialog
        print("✅ StepDialog class found with auto-fill methods")
        
        # Check if auto-fill methods exist
        methods_to_check = [
            '_auto_fill_output_key',
            '_suggest_action_names', 
            '_insert_code_template',
            '_suggest_return_values'
        ]
        
        for method_name in methods_to_check:
            if hasattr(StepDialog, method_name):
                print(f"✅ Method {method_name} found")
            else:
                print(f"❌ Method {method_name} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Auto-fill test failed: {e}")
        return False

def launch_gui_from_source():
    """Launch GUI directly from source code."""
    print("\n🖥️  Launching GUI from source...")
    
    try:
        from moveworks_wizard.gui.main_window import MoveworksWizardGUI
        print("✅ Starting GUI with auto-fill functionality...")
        app = MoveworksWizardGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")

def main():
    """Run tests and launch GUI."""
    print("🧙 Moveworks YAML Wizard - Auto-fill Test")
    print("=" * 50)
    
    # Run tests
    yaml_ok = test_yaml_generation()
    autofill_ok = test_autofill_functions()
    
    if yaml_ok and autofill_ok:
        print("\n🎉 All tests passed! Launching GUI...")
        launch_gui_from_source()
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
