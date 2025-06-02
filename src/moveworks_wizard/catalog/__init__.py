"""
Catalog module for Moveworks Compound Action Wizard.

This module provides catalogs and reference information for creating
compound actions, including built-in actions and common patterns.
"""

from .builtin_actions import BuiltinActionCatalog, BuiltinAction, ActionParameter, builtin_catalog

__all__ = [
    "BuiltinActionCatalog",
    "BuiltinAction", 
    "ActionParameter",
    "builtin_catalog"
]
