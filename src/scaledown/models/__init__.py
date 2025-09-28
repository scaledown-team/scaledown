"""
ScaleDown models module.

This module provides model interfaces and implementations for various AI providers.
"""

from .base_model import BaseModel
from .llm_model import LLMModel, LLMModelFactory

# Import LLM providers from tools for integration
try:
    from ..tools.llms import LLMProviderFactory, LLM
    __all__ = [
        'BaseModel',
        'LLMModel',
        'LLMModelFactory',
        'LLMProviderFactory',
        'LLM'
    ]
except ImportError:
    __all__ = [
        'BaseModel',
        'LLMModel',
        'LLMModelFactory'
    ]