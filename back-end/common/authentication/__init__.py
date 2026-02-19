"""
Authentication modules for application component creation and configuration.

This package contains authentication classes and utilities for creating and configuring
various application components in a clean, testable way.
"""

from .workspace import WorkspaceAuthentication
from .sql import SQLAuthentication

__all__ = ["WorkspaceAuthentication", "SQLAuthentication"]
