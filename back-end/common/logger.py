"""
Simple logging utility to avoid circular imports.
Uses LOG_LEVEL env var (default INFO). Set LOG_LEVEL=DEBUG to see debug messages.
Logs go to stderr so they appear in the terminal when running uvicorn.
"""

import logging
import os
import sys

# Create a logger instance that can be imported without circular dependencies
logger = logging.getLogger("databricks_app")
log_level_name = (os.environ.get("LOG_LEVEL") or "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logger.setLevel(log_level)

# If no handlers exist, add a console handler (stderr so it's visible and unbuffered)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Create an object that mimics the factory pattern for compatibility
class Logger:
    def __init__(self):
        self.logging = logger

    def info(self, message, *args, **kwargs):
        self.logging.info(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.logging.error(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.logging.warning(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.logging.debug(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        """Log at ERROR level and include exception traceback."""
        self.logging.exception(message, *args, **kwargs)

# Create instance for import
log = Logger()
