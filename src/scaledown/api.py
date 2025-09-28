from typing import Dict, List, Optional, Union, Any
import json

from .templates import Template, TemplateManager, get_default_manager as get_default_template_manager
from .styles import (
    Style, StyleManager, get_default_style_manager, get_enhanced_style_manager,
    OptimizationStyle, get_optimization_style_by_optimizers
)

class ScaleDown:
    """Main interface for the ScaleDown package."""
    
    def __init__(self, enable_optimization_styles: bool = True):
        """Initialize ScaleDown with default managers."""
        self.template_manager = get_default_template_manager()
        self.style_manager = get_enhanced_style_manager() if enable_optimization_styles else get_default_style_manager()
        self.current_template = None
        self.current_style = None
        self.current_model = None
        self.template_values = {}
        self.optimization_enabled = enable_optimization_styles
    
    def load(self, item_type: str) -> List[Dict[str, str]]:
        """Load templates, styles, or models.
        
        Args:
            item_type: Type of items to load ("templates", "styles", or "models")
            
        Returns:
            List of items with their id, name, and description
        """
        if item_type.lower() == "templates":
            return [{"id": t.id, "title": t.title, "description": t.template_text} 
                    for t in self.template_manager.list_templates()]
        
        elif item_type.lower() == "styles":
            return [{"id": s.id, "name": s.name, "description": s.description} 
                    for s in self.style_manager.list_styles()]
        
        elif item_type.lower() == "models":
            # Just return dummy models for testing
            return [
                {"id": "claude-3", "name": "Claude 3", "description": "Anthropic's Claude 3"},
                {"id": "gpt-4", "name": "GPT-4", "description": "OpenAI's GPT-4"}
            ]
        
        elif item_type.lower() == "expert_domains":
            from .styles.default_styles import EXPERT_DOMAINS
            return [{"id": d.lower(), "name": d, "description": f"Expert domain: {d}"} for d in EXPERT_DOMAINS]
        
        elif item_type.lower() == "expert_roles":
            from .styles.default_styles import EXPERT_ROLES
            return [{"id": r.lower(), "name": r, "description": f"Expert role: {r}"} for r in EXPERT_ROLES]
        
        else:
            raise ValueError(f"Invalid item type: {item_type}. Choose from: templates, styles, models, expert_domains, expert_roles")
    
    def select_template(self, template_id: str) -> Template:
        """Select a template by ID."""
        template = self.template_manager.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        self.current_template = template
        # Reset template values when changing templates
        self.template_values = {}
        
        return template
    
    def select_style(self, style_id: str) -> Style:
        """Select a style by ID."""
        style = self.style_manager.get_style(style_id)
        if not style:
            raise ValueError(f"Style not found: {style_id}")
        
        self.current_style = style
        return style
    
    def create_expert_style(self, domain: str, role: str, expertise_level: int = 85) -> Style:
        """Create and select a custom expert style."""
        style = self.style_manager.create_expert_style(domain, role, expertise_level)
        self.current_style = style
        return style
    
    def set_value(self, key: str, value: str) -> None:
        """Set a value for a template variable."""
        self.template_values[key] = value
    
    def set_values(self, values: Dict[str, str]) -> None:
        """Set multiple values for template variables."""
        self.template_values.update(values)
    
    def get_prompt(self) -> str:
        """Generate a prompt using the current template, values, and style."""
        if not self.current_template:
            raise ValueError("No template selected. Call select_template() first.")
        
        # Check for missing placeholders
        placeholders = self.current_template.placeholders
        missing = [p for p in placeholders if p not in self.template_values]
        if missing:
            raise ValueError(f"Missing values for placeholders: {', '.join(missing)}")
        
        # Render the template
        prompt = self.current_template.render(**self.template_values)
        
        # Apply style if one is selected
        if self.current_style:
            prompt = self.current_style.apply_to_prompt(prompt)
        
        return prompt
    
    def mock_optimize(self, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Mock optimization function for testing."""
        if prompt is None:
            prompt = self.get_prompt()
        
        # Just pretend to optimize by removing some filler words
        optimized = prompt.replace("Please ", "").replace("kindly ", "").replace("Could you ", "")
        
        # Mock token counts (just count words as a proxy for tokens)
        original_count = len(prompt.split())
        optimized_count = len(optimized.split())
        saved_tokens = original_count - optimized_count
        saved_percentage = (saved_tokens / original_count * 100) if original_count > 0 else 0
        
        return {
            "original": prompt,
            "optimized": optimized,
            "original_tokens": original_count,
            "optimized_tokens": optimized_count,
            "saved_tokens": saved_tokens,
            "saved_percentage": saved_percentage,
            "model": "mock-model"
        }

    def select_model(self, model_name: str, temperature: float = 0.0,
                    configuration: Optional[Dict[str, str]] = None) -> None:
        """Select and configure an LLM model.

        Args:
            model_name: Name/identifier of the model
            temperature: Temperature setting
            configuration: Configuration dict for API keys etc.
        """
        try:
            from .models.llm_model import LLMModelFactory
            self.current_model = LLMModelFactory.create_model(
                model_name=model_name,
                temperature=temperature,
                configuration=configuration
            )
        except ImportError:
            # Fallback if LLM integration not available
            self.current_model = None

    def optimize_with_pipeline(self, question: str, optimizers: List[str]) -> Dict[str, Any]:
        """Optimize question using the modular optimization pipeline.

        Args:
            question: The question or prompt to optimize
            optimizers: List of optimizer names to apply

        Returns:
            Dictionary with optimization results
        """
        if self.current_template:
            # Use template system if template is selected
            prompt = self.get_prompt()
        else:
            # Direct optimization
            prompt = question

        try:
            from .optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            optimized_prompt = registry.apply_optimizers(prompt, optimizers)
            report = registry.get_optimization_report(prompt, optimized_prompt, optimizers)

            return report
        except ImportError:
            # Fallback
            return {
                "original_prompt": prompt,
                "optimized_prompt": prompt,
                "optimizers_applied": optimizers,
                "optimization_count": 0
            }

    def optimize_and_call_llm(self, question: str, optimizers: List[str],
                             max_tokens: int = 1000) -> Dict[str, Any]:
        """Optimize prompt and call LLM in one step.

        Args:
            question: The question or prompt
            optimizers: List of optimizer names to apply
            max_tokens: Maximum tokens for response

        Returns:
            Dictionary with optimization info and LLM response
        """
        if not self.current_model:
            raise ValueError("No model selected. Call select_model() first.")

        if self.current_template:
            prompt = self.get_prompt()
        else:
            prompt = question

        return self.current_model.optimize_and_call(prompt, optimizers, max_tokens)

    def select_optimization_style(self, optimizers: List[str]) -> Optional[OptimizationStyle]:
        """Select an optimization style based on optimizer list.

        Args:
            optimizers: List of optimizer names

        Returns:
            OptimizationStyle if found/created, None otherwise
        """
        style = get_optimization_style_by_optimizers(optimizers)
        if style:
            self.current_style = style
        return style

    def list_optimizers(self) -> List[Dict[str, str]]:
        """List available prompt optimizers.

        Returns:
            List of optimizer information
        """
        try:
            from .optimization.prompt_optimizers import get_optimizer_registry
            registry = get_optimizer_registry()
            optimizers = []
            for name in registry.list_optimizers():
                info = registry.get_optimizer_info(name)
                if info:
                    optimizers.append(info)
            return optimizers
        except ImportError:
            return []

    def get_optimization_styles(self) -> List[Dict[str, Any]]:
        """Get available optimization styles.

        Returns:
            List of optimization style information
        """
        try:
            from .styles.optimization_style import create_default_optimization_styles
            styles = create_default_optimization_styles()
            return [style.to_dict() for style in styles]
        except ImportError:
            return []