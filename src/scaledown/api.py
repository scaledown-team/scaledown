from typing import Dict, List, Optional, Union, Any
import json

from .templates import Template, TemplateManager, get_default_manager as get_default_template_manager
from .styles import Style, StyleManager, get_default_style_manager

class ScaleDown:
    """Main interface for the ScaleDown package."""
    
    def __init__(self):
        """Initialize ScaleDown with default managers."""
        self.template_manager = get_default_template_manager()
        self.style_manager = get_default_style_manager()
        self.current_template = None
        self.current_style = None
        self.template_values = {}
    
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