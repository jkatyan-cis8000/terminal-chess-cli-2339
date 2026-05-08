"""
Cross-cutting concerns: input, output, and other infrastructure.

Providers provide interfaces that higher layers implement or that lower
layers can depend on without creating circular dependencies.
"""

from .input import InputProvider
from .output import OutputProvider

__all__ = ["InputProvider", "OutputProvider"]
