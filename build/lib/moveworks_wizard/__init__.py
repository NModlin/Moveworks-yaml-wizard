"""
Moveworks YAML Wizard for Compound Actions - Phase 4: Advanced Features & UI Enhancement

A Python application that provides a comprehensive wizard interface for creating
valid Moveworks Compound Action YAML files, specifically designed for use within
"Action Activities" in the post-April 2025 Plugin architecture.

Phase 4 Features:
- Comprehensive built-in action catalog (15+ actions across 8 categories)
- Template library with 8 pre-built workflow templates
- AI-powered action suggestions based on natural language descriptions
- Bender (Data Mapping Language) assistance for expressions
- GUI interface with tkinter for enhanced user experience
- Enhanced CLI with multiple start options and validation tools
"""

__version__ = "1.0.0-phase4"
__author__ = "Moveworks YAML Wizard Team"

from .models import *
from .wizard import *
from .serializers import *

# Phase 4 feature imports
try:
    from .catalog import builtin_catalog
    from .templates import template_library
    from .ai import action_suggester
    from .bender import bender_assistant
except ImportError:
    # Graceful fallback if Phase 4 modules are not available
    pass
