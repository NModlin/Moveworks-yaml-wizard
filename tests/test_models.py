"""
Tests for Moveworks Compound Action models.
"""

import pytest
from src.moveworks_wizard.models.base import CompoundAction
from src.moveworks_wizard.models.actions import ActionStep, ScriptStep
from src.moveworks_wizard.models.common import DelayConfig, ProgressUpdates


class TestCompoundAction:
    """Test cases for CompoundAction model."""
    
    def test_create_empty_compound_action(self):
        """Test creating an empty compound action."""
        # This should fail validation since we need either steps or single_step
        with pytest.raises(ValueError):
            CompoundAction()
    
    def test_create_compound_action_with_single_step(self):
        """Test creating a compound action with a single step."""
        step = ActionStep(action_name="test_action", output_key="test_output")
        
        compound_action = CompoundAction(
            name="Test Action",
            description="A test compound action",
            single_step=step
        )
        
        assert compound_action.name == "Test Action"
        assert compound_action.description == "A test compound action"
        assert compound_action.single_step == step
        assert compound_action.steps is None
        assert compound_action.get_step_count() == 1
    
    def test_create_compound_action_with_multiple_steps(self):
        """Test creating a compound action with multiple steps."""
        step1 = ActionStep(action_name="action1", output_key="output1")
        step2 = ActionStep(action_name="action2", output_key="output2")
        
        compound_action = CompoundAction(
            name="Multi-step Action",
            steps=[step1, step2]
        )
        
        assert compound_action.name == "Multi-step Action"
        assert len(compound_action.steps) == 2
        assert compound_action.single_step is None
        assert compound_action.get_step_count() == 2
    
    def test_add_step_to_single_step_action(self):
        """Test adding a step to a compound action that has a single step."""
        step1 = ActionStep(action_name="action1", output_key="output1")
        step2 = ActionStep(action_name="action2", output_key="output2")
        
        compound_action = CompoundAction(single_step=step1)
        compound_action.add_step(step2)
        
        assert compound_action.single_step is None
        assert len(compound_action.steps) == 2
        assert compound_action.get_step_count() == 2
    
    def test_to_yaml_dict_single_step(self):
        """Test YAML serialization for single step compound action."""
        step = ActionStep(action_name="test_action", output_key="test_output")
        compound_action = CompoundAction(single_step=step)
        
        yaml_dict = compound_action.to_yaml_dict()
        
        assert "action" in yaml_dict
        assert yaml_dict["action"]["action_name"] == "test_action"
        assert yaml_dict["action"]["output_key"] == "test_output"
    
    def test_to_yaml_dict_multiple_steps(self):
        """Test YAML serialization for multiple steps compound action."""
        step1 = ActionStep(action_name="action1", output_key="output1")
        step2 = ActionStep(action_name="action2", output_key="output2")
        
        compound_action = CompoundAction(steps=[step1, step2])
        
        yaml_dict = compound_action.to_yaml_dict()
        
        assert "steps" in yaml_dict
        assert len(yaml_dict["steps"]) == 2
        assert yaml_dict["steps"][0]["action"]["action_name"] == "action1"
        assert yaml_dict["steps"][1]["action"]["action_name"] == "action2"


class TestActionStep:
    """Test cases for ActionStep model."""
    
    def test_create_basic_action_step(self):
        """Test creating a basic action step."""
        step = ActionStep(action_name="test_action", output_key="test_output")
        
        assert step.action_name == "test_action"
        assert step.output_key == "test_output"
        assert step.get_step_type() == "action"
        assert not step.is_builtin_action()
    
    def test_create_builtin_action_step(self):
        """Test creating a built-in action step."""
        step = ActionStep(action_name="mw.create_ticket", output_key="ticket_output")
        
        assert step.action_name == "mw.create_ticket"
        assert step.is_builtin_action()
    
    def test_action_step_with_input_args(self):
        """Test action step with input arguments."""
        input_args = {
            "user_id": "data.user.id",
            "message": "Hello World"
        }
        
        step = ActionStep(
            action_name="send_message",
            output_key="message_result",
            input_args=input_args
        )
        
        assert step.input_args == input_args
    
    def test_action_step_with_delay_config(self):
        """Test action step with delay configuration."""
        delay_config = DelayConfig(seconds=10, minutes=1)
        
        step = ActionStep(
            action_name="delayed_action",
            output_key="delayed_output",
            delay_config=delay_config
        )
        
        assert step.delay_config == delay_config
    
    def test_action_step_to_yaml_dict(self):
        """Test YAML serialization for action step."""
        step = ActionStep(
            action_name="test_action",
            output_key="test_output",
            input_args={"param1": "value1"}
        )
        
        yaml_dict = step.to_yaml_dict()
        
        assert "action" in yaml_dict
        action_dict = yaml_dict["action"]
        assert action_dict["action_name"] == "test_action"
        assert action_dict["output_key"] == "test_output"
        assert action_dict["input_args"]["param1"] == "value1"


class TestScriptStep:
    """Test cases for ScriptStep model."""
    
    def test_create_basic_script_step(self):
        """Test creating a basic script step."""
        step = ScriptStep(
            code="return 'Hello World'",
            output_key="script_output"
        )
        
        assert step.code == "return 'Hello World'"
        assert step.output_key == "script_output"
        assert step.get_step_type() == "script"
        assert not step.is_multiline_code()
    
    def test_create_multiline_script_step(self):
        """Test creating a script step with multiline code."""
        code = """
x = 1 + 2
y = x * 3
return y
        """.strip()
        
        step = ScriptStep(code=code, output_key="calc_result")
        
        assert step.is_multiline_code()
        assert "x = 1 + 2" in step.code
    
    def test_script_step_to_yaml_dict(self):
        """Test YAML serialization for script step."""
        step = ScriptStep(
            code="return data.value * 2",
            output_key="doubled_value",
            input_args={"value": "data.input_number"}
        )
        
        yaml_dict = step.to_yaml_dict()
        
        assert "script" in yaml_dict
        script_dict = yaml_dict["script"]
        assert script_dict["code"] == "return data.value * 2"
        assert script_dict["output_key"] == "doubled_value"
        assert script_dict["input_args"]["value"] == "data.input_number"
