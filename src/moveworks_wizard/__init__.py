"""
Moveworks YAML Wizard for Compound Actions

A Python application that provides a user-friendly wizard interface for creating 
valid Moveworks Compound Action YAML files, specifically designed for use within 
"Action Activities" in the post-April 2025 Plugin architecture.
"""

__version__ = "0.1.0"
__author__ = "Moveworks YAML Wizard Team"

from .models import *
from .wizard import *
from .serializers import *
