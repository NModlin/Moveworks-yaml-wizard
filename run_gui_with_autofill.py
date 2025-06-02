#!/usr/bin/env python3
"""
Launch GUI with auto-fill functionality from source code.
This script ensures the GUI uses the latest source code with auto-fill features.
"""

import sys
import os
from pathlib import Path

def setup_source_path():
    """Ensure source code is used instead of installed package."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    src_path = script_dir / "src"
    
    # Remove any existing moveworks_wizard from sys.modules to force reload
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('moveworks_wizard')]
    for module in modules_to_remove:
        del sys.modules[module]
    
    # Insert source path at the beginning to ensure it takes precedence
    if str(src_path) in sys.path:
        sys.path.remove(str(src_path))
    sys.path.insert(0, str(src_path))
    
    print(f"✅ Using source code from: {src_path}")
    return src_path

def verify_autofill_features():
    """Verify that auto-fill features are available."""
    try:
        from moveworks_wizard.gui.main_window import StepDialog
        
        # Check for auto-fill methods
        autofill_methods = [
            '_auto_fill_output_key',
            '_suggest_action_names', 
            '_insert_code_template',
            '_suggest_return_values',
            '_on_step_type_changed',
            '_on_action_name_changed'
        ]
        
        missing_methods = []
        for method in autofill_methods:
            if not hasattr(StepDialog, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing auto-fill methods: {missing_methods}")
            return False
        else:
            print("✅ All auto-fill methods found!")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_yaml_generation():
    """Test YAML generation to ensure it's working correctly."""
    try:
        from moveworks_wizard.models.base import CompoundAction
        from moveworks_wizard.models.actions import ActionStep
        from moveworks_wizard.serializers import serialize_compound_action
        
        # Create a simple test
        step = ActionStep(
            action_name="test_action",
            output_key="test_result"
        )
        
        compound_action = CompoundAction(
            name="Test Action",
            steps=[step]
        )
        
        yaml_content = serialize_compound_action(compound_action)
        
        # Check if YAML starts with 'steps:' (correct order)
        if yaml_content.strip().startswith('steps:'):
            print("✅ YAML ordering is correct (steps first)")
            return True
        else:
            print("❌ YAML ordering issue detected")
            print(f"YAML starts with: {yaml_content.strip()[:50]}...")
            return False
            
    except Exception as e:
        print(f"❌ YAML test failed: {e}")
        return False

def launch_gui():
    """Launch the GUI with auto-fill functionality."""
    try:
        from moveworks_wizard.gui.main_window import MoveworksWizardGUI
        
        print("\n🖥️  Launching Moveworks Wizard GUI with Auto-fill Features...")
        print("=" * 60)
        print("Auto-fill features available:")
        print("• Output Key: Click 'Auto' button to generate from action name")
        print("• Action Name: Click 'Suggest' for built-in actions")
        print("• Code: Click 'Template' for code templates")
        print("• Return Value: Click 'Suggest' for common patterns")
        print("=" * 60)
        
        app = MoveworksWizardGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to set up and launch GUI."""
    print("🧙 Moveworks YAML Wizard - Auto-fill Edition")
    print("=" * 50)
    
    # Setup source path
    setup_source_path()
    
    # Verify features
    autofill_ok = verify_autofill_features()
    yaml_ok = test_yaml_generation()
    
    if autofill_ok and yaml_ok:
        print("\n🎉 All systems ready!")
        launch_gui()
    else:
        print("\n⚠️  Some issues detected. Launching anyway...")
        launch_gui()

if __name__ == "__main__":
    main()
