"""
Observation utilities.

This package surfaces lightweight instrumentation helpers (logging, metrics),
keeping dependencies to the standard library for now.
"""

from .logging import configure_logging, get_logger, StructuredLogger

__all__ = ["configure_logging", "get_logger", "StructuredLogger"]
