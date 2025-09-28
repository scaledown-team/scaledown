"""
LLM Model implementation that integrates with the tools/llms.py providers.
"""
from typing import Dict, Any, List, Optional
try:
    import tiktoken
except ImportError:
    tiktoken = None

from .base_model import BaseModel
from ..tools.llms import LLMProviderFactory, LLM


class LLMModel(BaseModel):
    """Model implementation that wraps the LLM providers from tools/llms.py."""

    def __init__(self, model_name: str, temperature: float = 0.0, configuration: Optional[Dict[str, str]] = None, **kwargs):
        """Initialize LLM model.

        Args:
            model_name: Name/identifier of the model
            temperature: Temperature setting for the model
            configuration: Configuration dict for API keys etc.
            **kwargs: Additional model-specific configuration
        """
        super().__init__(model_name, **kwargs)
        self.temperature = temperature
        self.configuration = configuration or {}

        # Create the underlying LLM provider
        self.llm_provider = LLMProviderFactory.create_provider(
            model_id=model_name,
            temperature=temperature,
            configuration=self.configuration
        )

    def optimize_prompt(self, prompt: str) -> str:
        """Basic semantic optimization using patterns."""
        try:
            from ..optimization.semantic_optimizer import SemanticOptimizer
            optimizer = SemanticOptimizer()
            return optimizer.optimize(prompt)
        except ImportError:
            # Fallback to simple optimization
            return prompt.replace("Please ", "").replace("Could you ", "")

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken for OpenAI models or approximation for others."""
        try:
            if tiktoken and "gpt" in self.model_name.lower():
                # Use tiktoken for OpenAI models if available
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                return len(encoding.encode(text))
            else:
                # Approximation: 1 token ≈ 4 characters
                return len(text) // 4
        except Exception:
            # Fallback: word count approximation
            return len(text.split())

    def get_token_limit(self) -> int:
        """Get the token limit for this model."""
        model_limits = {
            "gpt-4": 8192,
            "gpt-3.5-turbo": 4096,
            "gemini-1.5-flash": 1048576,
            "gemini-2.5-flash-lite": 1048576,
            "scaledown-gpt-4o": 128000
        }

        # Find matching model
        for model_key, limit in model_limits.items():
            if model_key in self.model_name.lower():
                return limit

        # Default limit
        return 4096

    def call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call the underlying LLM provider."""
        return self.llm_provider.call_llm(prompt, max_tokens)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        base_info = self.llm_provider.get_model_info()
        base_info.update({
            "token_limit": self.get_token_limit(),
            "temperature": self.temperature,
            "has_optimization_pipeline": True
        })
        return base_info

    def optimize_and_call(self, prompt: str, optimizers: List[str], max_tokens: int = 1000) -> Dict[str, Any]:
        """Optimize prompt with pipeline and call LLM.

        Args:
            prompt: Original prompt
            optimizers: List of optimizer names to apply
            max_tokens: Maximum tokens for response

        Returns:
            Dictionary with optimization info and LLM response
        """
        # Get optimization report
        optimization_report = self.get_optimization_report(prompt, optimizers)
        optimized_prompt = optimization_report["optimized_prompt"]

        # Call LLM with optimized prompt
        response = self.call_llm(optimized_prompt, max_tokens)

        # Return comprehensive result
        return {
            "original_prompt": prompt,
            "optimized_prompt": optimized_prompt,
            "optimizers_applied": optimizers,
            "optimization_metrics": optimization_report,
            "llm_response": response,
            "model_info": self.get_model_info()
        }


class LLMModelFactory:
    """Factory for creating LLM models with optimization pipeline."""

    @staticmethod
    def create_model(model_name: str, temperature: float = 0.0,
                    configuration: Optional[Dict[str, str]] = None) -> LLMModel:
        """Create an LLM model instance.

        Args:
            model_name: Name/identifier of the model
            temperature: Temperature setting
            configuration: Configuration dict

        Returns:
            LLMModel instance
        """
        return LLMModel(
            model_name=model_name,
            temperature=temperature,
            configuration=configuration
        )

    @staticmethod
    def list_supported_models() -> List[str]:
        """List supported model names."""
        return [
            "scaledown-gpt-4o",
            "gpt-4",
            "gpt-3.5-turbo",
            "gemini-1.5-flash",
            "gemini-2.5-flash-lite"
        ]