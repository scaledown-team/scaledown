"""
Optimization styles that integrate with the modular prompt optimization pipeline.
"""
from typing import List, Dict, Any, Optional
from .style import Style


class OptimizationStyle(Style):
    """Style that applies prompt optimization techniques."""

    def __init__(self, id: str, name: str, description: str,
                 optimizers: List[str], icon: str = "⚡",
                 template_modifier: str = "", system_prompt: str = ""):
        """Initialize optimization style.

        Args:
            id: Unique identifier for the style
            name: Display name
            description: Description of the optimization
            optimizers: List of optimizer names to apply
            icon: Icon for the style
            template_modifier: Additional template modifier
            system_prompt: System prompt if needed
        """
        super().__init__(id, name, description, icon, template_modifier, system_prompt)
        self.optimizers = optimizers

    def apply_to_prompt(self, prompt_text: str) -> str:
        """Apply optimization to the prompt."""
        # First apply any template modifier from parent
        result = super().apply_to_prompt(prompt_text)

        # Then apply the optimization pipeline
        try:
            from ..optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            result = registry.apply_optimizers(result, self.optimizers)
        except ImportError:
            # Fallback if optimization pipeline not available
            pass

        return result

    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about the optimizations applied."""
        try:
            from ..optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            return {
                "optimizers": self.optimizers,
                "optimizer_details": [
                    registry.get_optimizer_info(opt) for opt in self.optimizers
                    if registry.get_optimizer_info(opt)
                ]
            }
        except ImportError:
            return {"optimizers": self.optimizers}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with optimization info."""
        base_dict = super().to_dict()
        base_dict.update({
            "optimizers": self.optimizers,
            "style_type": "optimization"
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationStyle':
        """Create optimization style from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            optimizers=data.get("optimizers", []),
            icon=data.get("icon", "⚡"),
            template_modifier=data.get("template_modifier", ""),
            system_prompt=data.get("system_prompt", "")
        )


def create_default_optimization_styles() -> List[OptimizationStyle]:
    """Create default optimization styles based on available optimizers."""
    return [
        OptimizationStyle(
            id="expert_thinking",
            name="Expert Thinking",
            description="Combines expert persona with step-by-step reasoning",
            optimizers=["expert_persona", "cot"],
            icon="🧠"
        ),
        OptimizationStyle(
            id="verified_expert",
            name="Verified Expert",
            description="Expert persona with verification process to reduce errors",
            optimizers=["expert_persona", "cove"],
            icon="✅"
        ),
        OptimizationStyle(
            id="careful_reasoning",
            name="Careful Reasoning",
            description="Step-by-step reasoning with confidence assessment",
            optimizers=["cot", "uncertainty"],
            icon="🔍"
        ),
        OptimizationStyle(
            id="comprehensive_analysis",
            name="Comprehensive Analysis",
            description="Full optimization pipeline with all techniques",
            optimizers=["expert_persona", "cot", "uncertainty", "cove"],
            icon="🎯"
        ),
        OptimizationStyle(
            id="verification_focused",
            name="Verification Focused",
            description="Emphasizes verification to minimize hallucinations",
            optimizers=["cove", "uncertainty"],
            icon="🛡️"
        ),
        OptimizationStyle(
            id="expert_only",
            name="Expert Persona",
            description="Simple expert persona enhancement",
            optimizers=["expert_persona"],
            icon="👨‍🔬"
        ),
        OptimizationStyle(
            id="reasoning_only",
            name="Chain of Thought",
            description="Step-by-step reasoning without other enhancements",
            optimizers=["cot"],
            icon="🔗"
        ),
        OptimizationStyle(
            id="baseline",
            name="Baseline",
            description="No optimization applied (baseline comparison)",
            optimizers=["none"],
            icon="📊"
        )
    ]


def get_optimization_style_by_optimizers(optimizers: List[str]) -> Optional[OptimizationStyle]:
    """Get an optimization style that matches the given optimizers."""
    default_styles = create_default_optimization_styles()

    for style in default_styles:
        if set(style.optimizers) == set(optimizers):
            return style

    # Create a custom style if no match found
    if optimizers and optimizers != ["none"]:
        return OptimizationStyle(
            id="custom_" + "_".join(optimizers),
            name=f"Custom: {', '.join(optimizers)}",
            description=f"Custom optimization with: {', '.join(optimizers)}",
            optimizers=optimizers,
            icon="🔧"
        )

    return None