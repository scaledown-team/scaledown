# scaledown/models/model_registry.py

from typing import Dict, Type, List, Optional
import os

from .base_model import BaseModel
from .claude_model import ClaudeModel
from .openai_model import OpenAIModel


class ModelRegistry:
    """Registry for AI model implementations."""
    
    def __init__(self):
        """Initialize model registry."""
        self._model_classes: Dict[str, Type[BaseModel]] = {}
        self._model_groups: Dict[str, List[str]] = {}
        self._register_default_models()
    
    def _register_default_models(self):
        """Register default model implementations."""
        # Register model families
        self.register_model_class("claude", ClaudeModel)
        self.register_model_class("gpt", OpenAIModel)
        self.register_model_class("openai", OpenAIModel)  # Alias
        
        # Register Claude models
        claude_models = [
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-2.0",
            "claude-2.1",
        ]
        for model in claude_models:
            self.register_model_class(model, ClaudeModel)
        self._model_groups["claude"] = claude_models
            
        # Register OpenAI models
        openai_models = [
            "gpt-3.5-turbo", 
            "gpt-4",
            "gpt-4-turbo", 
            "gpt-4o",
            "gpt-4-vision",
        ]
        for model in openai_models:
            self.register_model_class(model, OpenAIModel)
        self._model_groups["openai"] = openai_models
        self._model_groups["gpt"] = openai_models
    
    def register_model_class(self, model_name: str, model_class: Type[BaseModel]) -> None:
        """Register a model implementation with the registry.
        
        Args:
            model_name: Name identifier for the model
            model_class: Class that implements the model
        """
        self._model_classes[model_name.lower()] = model_class
    
    def get_model_class(self, model_name: str) -> Optional[Type[BaseModel]]:
        """Get the model class for a given model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            The model class if found, None otherwise
        """
        model_key = model_name.lower()
        
        # Try exact match first
        if model_key in self._model_classes:
            return self._model_classes[model_key]
        
        # Try prefix match
        for registered_name, model_class in self._model_classes.items():
            if model_key.startswith(registered_name):
                return model_class
        
        return None
    
    def create_model(self, model_name: str, **kwargs) -> BaseModel:
        """Create a model instance.
        
        Args:
            model_name: Name of the model to create
            **kwargs: Additional arguments to pass to the model constructor
            
        Returns:
            Instance of the requested model
            
        Raises:
            ValueError: If the model is not registered
        """
        model_class = self.get_model_class(model_name)
        
        if model_class is None:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Look for API keys in environment if not provided
        if "api_key" not in kwargs:
            if model_class == ClaudeModel:
                kwargs["api_key"] = os.environ.get("ANTHROPIC_API_KEY")
            elif model_class == OpenAIModel:
                kwargs["api_key"] = os.environ.get("OPENAI_API_KEY")
        
        return model_class(model_name, **kwargs)
    
    def list_available_models(self, group: Optional[str] = None) -> List[str]:
        """List available models, optionally filtered by group.
        
        Args:
            group: Optional group name to filter by (e.g., "claude", "openai")
            
        Returns:
            List of model names
        """
        if group and group.lower() in self._model_groups:
            return self._model_groups[group.lower()]
        
        return list(sorted(self._model_classes.keys()))


# Create a singleton instance
model_registry = ModelRegistry()