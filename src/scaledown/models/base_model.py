from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from ..templates.template import Template


class BaseModel(ABC):
    """Base class for AI model integrations."""
    
    def __init__(self, model_name: str, **kwargs):
        """Initialize model with configuration.
        
        Args:
            model_name: Name/identifier of the model
            **kwargs: Additional model-specific configuration
        """
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def optimize_prompt(self, prompt: str) -> str:
        """Optimize a prompt for this specific model.
        
        Args:
            prompt: The original prompt
            
        Returns:
            The optimized prompt
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text for this model.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def get_token_limit(self) -> int:
        """Get the token limit for this model.
        
        Returns:
            Maximum number of tokens allowed
        """
        pass
    
    def optimize_template(self, template: Template, values: Dict[str, Any]) -> str:
        """Optimize a rendered template.
        
        Args:
            template: The template to render and optimize
            values: Values to fill the template placeholders
            
        Returns:
            The optimized prompt
        """
        rendered_prompt = template.render(**values)
        return self.optimize_prompt(rendered_prompt)
    
    def get_token_usage(self, text: str) -> Dict[str, Any]:
        """Get token usage information for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with token count and limit information
        """
        count = self.count_tokens(text)
        limit = self.get_token_limit()
        
        return {
            "count": count,
            "limit": limit,
            "percentage": (count / limit) * 100 if limit > 0 else 0,
            "remaining": limit - count
        }

    def optimize_prompt_with_pipeline(self, prompt: str, optimizers: List[str]) -> str:
        """Optimize prompt using the modular optimization pipeline.

        Args:
            prompt: The original prompt
            optimizers: List of optimizer names to apply

        Returns:
            The optimized prompt with optimizers applied
        """
        try:
            from ..optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            return registry.apply_optimizers(prompt, optimizers)
        except ImportError:
            # Fallback to basic optimization if pipeline not available
            return self.optimize_prompt(prompt)

    def get_optimization_report(self, original_prompt: str, optimizer_names: List[str]) -> Dict[str, Any]:
        """Generate optimization report using the pipeline.

        Args:
            original_prompt: The original prompt
            optimizer_names: List of optimizer names applied

        Returns:
            Optimization report with metrics
        """
        optimized_prompt = self.optimize_prompt_with_pipeline(original_prompt, optimizer_names)

        try:
            from ..optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            return registry.get_optimization_report(original_prompt, optimized_prompt, optimizer_names)
        except ImportError:
            # Fallback report
            return {
                "original_prompt": original_prompt,
                "optimized_prompt": optimized_prompt,
                "optimizers_applied": optimizer_names,
                "original_length": len(original_prompt),
                "optimized_length": len(optimized_prompt),
                "length_change": len(optimized_prompt) - len(original_prompt)
            }