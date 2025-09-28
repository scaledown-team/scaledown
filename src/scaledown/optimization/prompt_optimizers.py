"""
Modular prompt optimization system integrating with ScaleDown framework.
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..tools.prompts import (
    EXPERT_PERSONA_PROMPT,
    COT_PROMPT,
    UNCERTAINTY_PROMPT,
    COVE_PROMPT
)


class BasePromptOptimizer(ABC):
    """Base class for prompt optimizers."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def apply(self, prompt: str) -> str:
        """Apply optimization to the prompt."""
        pass

    def get_info(self) -> Dict[str, str]:
        """Get optimizer information."""
        return {
            "name": self.name,
            "description": self.description
        }


class ExpertPersonaOptimizer(BasePromptOptimizer):
    """Expert persona optimization - adds domain expertise context."""

    def __init__(self):
        super().__init__(
            name="expert_persona",
            description="Adds domain expert persona for more accurate responses"
        )

    def apply(self, prompt: str) -> str:
        return f"{EXPERT_PERSONA_PROMPT}\n\n{prompt}"


class ChainOfThoughtOptimizer(BasePromptOptimizer):
    """Chain-of-thought optimization - adds step-by-step reasoning."""

    def __init__(self):
        super().__init__(
            name="cot",
            description="Enables step-by-step reasoning process"
        )

    def apply(self, prompt: str) -> str:
        return f"{prompt}\n\n{COT_PROMPT}"


class UncertaintyOptimizer(BasePromptOptimizer):
    """Uncertainty quantification - adds confidence assessment."""

    def __init__(self):
        super().__init__(
            name="uncertainty",
            description="Adds confidence level assessment to responses"
        )

    def apply(self, prompt: str) -> str:
        return f"{prompt}\n\n{UNCERTAINTY_PROMPT}"


class ChainOfVerificationOptimizer(BasePromptOptimizer):
    """Chain-of-verification optimization - adds verification process."""

    def __init__(self):
        super().__init__(
            name="cove",
            description="Adds verification process to reduce hallucinations"
        )

    def apply(self, prompt: str) -> str:
        return f"{prompt}\n\n{COVE_PROMPT}"


class NoneOptimizer(BasePromptOptimizer):
    """No optimization - baseline prompt."""

    def __init__(self):
        super().__init__(
            name="none",
            description="No optimization applied (baseline)"
        )

    def apply(self, prompt: str) -> str:
        return prompt


class PromptOptimizerRegistry:
    """Registry for managing prompt optimizers."""

    def __init__(self):
        self.optimizers = {
            "expert_persona": ExpertPersonaOptimizer(),
            "cot": ChainOfThoughtOptimizer(),
            "uncertainty": UncertaintyOptimizer(),
            "cove": ChainOfVerificationOptimizer(),
            "none": NoneOptimizer()
        }

    def get_optimizer(self, name: str) -> Optional[BasePromptOptimizer]:
        """Get optimizer by name."""
        return self.optimizers.get(name)

    def list_optimizers(self) -> List[str]:
        """List all available optimizer names."""
        return list(self.optimizers.keys())

    def get_optimizer_info(self, name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific optimizer."""
        optimizer = self.get_optimizer(name)
        return optimizer.get_info() if optimizer else None

    def parse_optimizers(self, optimizers_string: str) -> List[str]:
        """Parse comma-separated optimizer string into list of optimizer names."""
        if not optimizers_string:
            return []

        optimizers = [opt.strip() for opt in optimizers_string.split(",")]

        # Validate all optimizers exist
        invalid_optimizers = [opt for opt in optimizers if opt not in self.optimizers]
        if invalid_optimizers:
            valid_opts = ", ".join(self.optimizers.keys())
            raise ValueError(f"Invalid optimizers: {invalid_optimizers}. Valid options: {valid_opts}")

        return optimizers

    def apply_optimizers(self, prompt: str, optimizer_names: List[str]) -> str:
        """Apply multiple optimizers in sequence to a prompt."""
        if not optimizer_names:
            return prompt

        result = prompt
        applied_optimizers = []

        # Handle expert_persona specially (always goes first)
        if "expert_persona" in optimizer_names:
            expert_optimizer = self.get_optimizer("expert_persona")
            result = expert_optimizer.apply(result)
            applied_optimizers.append("expert_persona")

        # Apply other optimizers in the order specified
        for optimizer_name in optimizer_names:
            if optimizer_name in ["expert_persona", "none"]:
                continue

            optimizer = self.get_optimizer(optimizer_name)
            if optimizer:
                result = optimizer.apply(result)
                applied_optimizers.append(optimizer_name)

        return result

    def get_optimization_report(self, original_prompt: str, optimized_prompt: str,
                              optimizer_names: List[str]) -> Dict[str, Any]:
        """Generate a report about the optimization process."""
        return {
            "original_prompt": original_prompt,
            "optimized_prompt": optimized_prompt,
            "optimizers_applied": optimizer_names,
            "original_length": len(original_prompt),
            "optimized_length": len(optimized_prompt),
            "length_change": len(optimized_prompt) - len(original_prompt),
            "optimization_count": len([opt for opt in optimizer_names if opt != "none"])
        }


# Global registry instance
_global_registry = None

def get_optimizer_registry() -> PromptOptimizerRegistry:
    """Get the global optimizer registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PromptOptimizerRegistry()
    return _global_registry


# Convenience functions for backward compatibility
def optimize_prompt(question: str, optimizers_list: List[str]) -> str:
    """
    Build optimized prompt by applying the specified optimizers to a question.

    Args:
        question: The question to optimize
        optimizers_list: List of optimizer names to apply (can be empty)

    Returns:
        Optimized prompt with applied optimizers
    """
    registry = get_optimizer_registry()
    return registry.apply_optimizers(question, optimizers_list)


def parse_optimizers(optimizers_string: str) -> List[str]:
    """Parse comma-separated optimizer string into list of optimizer names."""
    registry = get_optimizer_registry()
    return registry.parse_optimizers(optimizers_string)


# Export optimizer prompts for backward compatibility
OPTIMIZER_PROMPTS = {
    "expert_persona": EXPERT_PERSONA_PROMPT,
    "cot": COT_PROMPT,
    "uncertainty": UNCERTAINTY_PROMPT,
    "cove": COVE_PROMPT,
    "none": ""
}