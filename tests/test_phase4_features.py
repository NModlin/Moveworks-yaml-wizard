"""
Phase 4 Feature Tests for Moveworks YAML Wizard

This module contains comprehensive tests for Phase 4 features including:
- Enhanced built-in action catalog
- Template library system
- AI-powered action suggestions
- Bender assistance for data mapping
- GUI components (basic tests)
"""

import pytest
from unittest.mock import patch, MagicMock

from src.moveworks_wizard.catalog.builtin_actions import builtin_catalog, BuiltinAction
from src.moveworks_wizard.templates.template_library import template_library, CompoundActionTemplate
from src.moveworks_wizard.ai.action_suggester import action_suggester, ActionSuggestion, SuggestionType
from src.moveworks_wizard.bender.bender_assistant import bender_assistant, BenderFunction, BenderExpression


class TestEnhancedBuiltinCatalog:
    """Test the enhanced built-in action catalog."""
    
    def test_catalog_has_expanded_actions(self):
        """Test that the catalog has been expanded with new actions."""
        all_actions = builtin_catalog.get_all_actions()
        assert len(all_actions) >= 15, "Should have at least 15 built-in actions"
        
        # Check for new categories
        categories = builtin_catalog.get_all_categories()
        expected_categories = [
            "Communication", "User Management", "Security & Access",
            "Ticket Management", "Approval Workflow", "Data Retrieval",
            "Integration & Automation", "Analytics & Reporting",
            "File & Document Management"
        ]
        
        for category in expected_categories:
            assert category in categories, f"Missing category: {category}"
    
    def test_new_security_actions(self):
        """Test new security and access management actions."""
        security_actions = builtin_catalog.get_actions_by_category("Security & Access")
        assert len(security_actions) >= 3, "Should have at least 3 security actions"
        
        action_names = [action.name for action in security_actions]
        assert "mw.check_user_permissions" in action_names
        assert "mw.grant_access" in action_names
        assert "mw.revoke_access" in action_names
    
    def test_new_integration_actions(self):
        """Test new integration and automation actions."""
        integration_actions = builtin_catalog.get_actions_by_category("Integration & Automation")
        assert len(integration_actions) >= 2, "Should have at least 2 integration actions"
        
        action_names = [action.name for action in integration_actions]
        assert "mw.trigger_webhook" in action_names
        assert "mw.schedule_task" in action_names
    
    def test_action_search_functionality(self):
        """Test enhanced search functionality."""
        # Search for webhook actions
        webhook_results = builtin_catalog.search_actions("webhook")
        assert len(webhook_results) > 0, "Should find webhook-related actions"
        
        # Search for notification actions
        notification_results = builtin_catalog.search_actions("notification")
        assert len(notification_results) >= 2, "Should find notification actions"


class TestTemplateLibrary:
    """Test the template library system."""
    
    def test_template_library_initialization(self):
        """Test that template library loads correctly."""
        all_templates = template_library.get_all_templates()
        assert len(all_templates) >= 8, "Should have at least 8 templates"
        
        categories = template_library.get_all_categories()
        expected_categories = [
            "User Management", "Security & Access", "Support & Ticketing",
            "Approval Workflow", "Data Processing"
        ]
        
        for category in expected_categories:
            assert category in categories, f"Missing template category: {category}"
    
    def test_user_management_templates(self):
        """Test user management templates."""
        user_templates = template_library.get_templates_by_category("User Management")
        assert len(user_templates) >= 2, "Should have at least 2 user management templates"
        
        template_names = [template.name for template in user_templates]
        assert "User Onboarding Workflow" in template_names
        assert "User Offboarding Workflow" in template_names
    
    def test_template_structure(self):
        """Test that templates have proper structure."""
        template = template_library.get_template("user_onboarding")
        assert template is not None, "User onboarding template should exist"
        
        assert isinstance(template, CompoundActionTemplate)
        assert template.name
        assert template.description
        assert template.category
        assert template.use_case
        assert template.compound_action
        assert template.customization_notes
        assert len(template.customization_notes) > 0
    
    def test_template_search(self):
        """Test template search functionality."""
        # Search for onboarding templates
        onboarding_results = template_library.search_templates("onboarding")
        assert len(onboarding_results) > 0, "Should find onboarding templates"
        
        # Search for approval templates
        approval_results = template_library.search_templates("approval")
        assert len(approval_results) >= 2, "Should find approval templates"


class TestAIActionSuggester:
    """Test the AI-powered action suggestion system."""
    
    def test_action_suggester_initialization(self):
        """Test that action suggester initializes correctly."""
        # Test keyword mappings
        assert hasattr(action_suggester, '_keywords')
        assert hasattr(action_suggester, '_patterns')
        
        # Check for expected keyword categories
        keywords = action_suggester._keywords
        expected_categories = [
            "communication", "user_management", "security_access",
            "ticket_management", "approval_workflow", "data_processing"
        ]
        
        for category in expected_categories:
            assert category in keywords, f"Missing keyword category: {category}"
    
    def test_communication_suggestions(self):
        """Test suggestions for communication-related descriptions."""
        description = "I need to send a notification to users about system maintenance"
        suggestions = action_suggester.suggest_actions(description, max_suggestions=3)
        
        assert len(suggestions) > 0, "Should provide suggestions for communication tasks"
        
        # Check that at least one suggestion is communication-related
        has_communication_suggestion = any(
            "notification" in suggestion.title.lower() or 
            "communication" in suggestion.description.lower()
            for suggestion in suggestions
        )
        assert has_communication_suggestion, "Should suggest communication actions"
    
    def test_user_management_suggestions(self):
        """Test suggestions for user management descriptions."""
        description = "I want to onboard a new employee and set up their access"
        suggestions = action_suggester.suggest_actions(description, max_suggestions=3)
        
        assert len(suggestions) > 0, "Should provide suggestions for user management"
        
        # Check for user management or onboarding suggestions
        has_user_mgmt_suggestion = any(
            "user" in suggestion.title.lower() or 
            "onboard" in suggestion.description.lower()
            for suggestion in suggestions
        )
        assert has_user_mgmt_suggestion, "Should suggest user management actions"
    
    def test_security_suggestions(self):
        """Test suggestions for security-related descriptions."""
        description = "I need to grant access permissions to a user for a specific system"
        suggestions = action_suggester.suggest_actions(description, max_suggestions=3)
        
        assert len(suggestions) > 0, "Should provide suggestions for security tasks"
        
        # Check for security or access-related suggestions
        has_security_suggestion = any(
            "access" in suggestion.title.lower() or 
            "permission" in suggestion.description.lower()
            for suggestion in suggestions
        )
        assert has_security_suggestion, "Should suggest security actions"
    
    def test_suggestion_confidence_scores(self):
        """Test that suggestions have reasonable confidence scores."""
        description = "send notification to user about ticket update"
        suggestions = action_suggester.suggest_actions(description)
        
        for suggestion in suggestions:
            assert 0.0 <= suggestion.confidence <= 1.0, "Confidence should be between 0 and 1"
            assert suggestion.reasoning, "Should provide reasoning for suggestions"


class TestBenderAssistant:
    """Test the Bender (Data Mapping Language) assistant."""
    
    def test_bender_assistant_initialization(self):
        """Test that Bender assistant initializes correctly."""
        # Test function catalog
        all_functions = bender_assistant.get_all_functions()
        assert len(all_functions) >= 6, "Should have at least 6 Bender functions"
        
        function_names = [func.name for func in all_functions]
        expected_functions = ["MAP", "CONCAT", "RENDER", "FILTER", "EXTRACT", "IF"]
        
        for func_name in expected_functions:
            assert func_name in function_names, f"Missing Bender function: {func_name}"
    
    def test_bender_function_details(self):
        """Test Bender function details."""
        map_function = bender_assistant.get_function("MAP")
        assert map_function is not None, "MAP function should exist"
        assert isinstance(map_function, BenderFunction)
        assert map_function.description
        assert map_function.example
        assert map_function.use_case
        assert len(map_function.parameters) > 0
    
    def test_common_patterns(self):
        """Test common Bender expression patterns."""
        all_patterns = bender_assistant.get_all_patterns()
        assert len(all_patterns) >= 6, "Should have at least 6 common patterns"
        
        # Test specific patterns
        user_name_pattern = bender_assistant.get_pattern("user_full_name")
        assert user_name_pattern is not None, "User full name pattern should exist"
        assert isinstance(user_name_pattern, BenderExpression)
        assert "CONCAT" in user_name_pattern.expression
    
    def test_expression_validation(self):
        """Test Bender expression validation."""
        # Valid expression
        valid_expr = "CONCAT(data.first_name, ' ', data.last_name)"
        result = bender_assistant.validate_expression(valid_expr)
        assert result['is_valid'], "Valid expression should pass validation"
        assert "CONCAT" in result['functions_used']
        
        # Invalid expression (unbalanced parentheses)
        invalid_expr = "CONCAT(data.first_name, ' ', data.last_name"
        result = bender_assistant.validate_expression(invalid_expr)
        assert not result['is_valid'], "Invalid expression should fail validation"
        assert len(result['errors']) > 0
    
    def test_expression_suggestions(self):
        """Test expression suggestions based on use case."""
        # Test name-related suggestions
        suggestions = bender_assistant.suggest_expression(
            "combine user name", 
            ["data.first_name", "data.last_name"]
        )
        assert len(suggestions) > 0, "Should suggest expressions for name combination"
        
        # Test email-related suggestions
        suggestions = bender_assistant.suggest_expression(
            "extract email domain",
            ["data.user_email"]
        )
        assert len(suggestions) > 0, "Should suggest expressions for email processing"


class TestGUIComponents:
    """Test basic GUI component functionality."""
    
    @pytest.mark.skipif(True, reason="GUI tests require display - skip in CI")
    def test_gui_import(self):
        """Test that GUI components can be imported."""
        try:
            from src.moveworks_wizard.gui.main_window import MoveworksWizardGUI
            assert MoveworksWizardGUI is not None
        except ImportError:
            pytest.skip("GUI dependencies not available")
    
    def test_gui_cli_command_exists(self):
        """Test that GUI CLI command exists."""
        from src.moveworks_wizard.wizard.cli import cli
        
        # Check that 'gui' command is registered
        commands = cli.commands
        assert 'gui' in commands, "GUI command should be available in CLI"


class TestPhase4Integration:
    """Test integration between Phase 4 features."""
    
    def test_cli_template_integration(self):
        """Test CLI integration with template library."""
        from src.moveworks_wizard.wizard.cli import CompoundActionWizard
        
        wizard = CompoundActionWizard()
        
        # Test that wizard can access template library
        categories = template_library.get_all_categories()
        assert len(categories) > 0, "Wizard should have access to templates"
    
    def test_cli_ai_integration(self):
        """Test CLI integration with AI suggestions."""
        from src.moveworks_wizard.wizard.cli import CompoundActionWizard
        
        wizard = CompoundActionWizard()
        
        # Test that wizard can access AI suggester
        suggestions = action_suggester.suggest_actions("test description")
        # Should not crash, even if no suggestions found
        assert isinstance(suggestions, list)
    
    def test_template_compound_action_validity(self):
        """Test that template compound actions are valid."""
        from src.moveworks_wizard.serializers import serialize_compound_action
        
        # Test a few templates
        template_names = ["user_onboarding", "access_request", "ticket_escalation"]
        
        for template_name in template_names:
            template = template_library.get_template(template_name)
            if template:
                # Should be able to serialize without errors
                yaml_content = serialize_compound_action(template.compound_action)
                assert yaml_content, f"Template {template_name} should serialize to valid YAML"
                assert "name:" in yaml_content
                assert "steps:" in yaml_content or "single_step:" in yaml_content


if __name__ == "__main__":
    pytest.main([__file__])
