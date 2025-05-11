from typing import Dict, List, Optional
from .template import Template

class TemplateManager:
    """Manager for template operations."""
    
    def __init__(self):
        """Initialize template manager."""
        self.templates: Dict[str, Template] = {}
        
    def add_template(self, template: Template) -> None:
        """Add a template to the manager."""
        if template.id in self.templates:
            raise ValueError(f"Template with ID '{template.id}' already exists")
        
        self.templates[template.id] = template
        
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None, 
                      subcategory: Optional[str] = None) -> List[Template]:
        """List templates, optionally filtered by category/subcategory."""
        results = list(self.templates.values())
        
        if category:
            results = [t for t in results if t.category == category]
            
        if subcategory:
            results = [t for t in results if t.subcategory == subcategory]
            
        return results
    
    def list_categories(self) -> List[str]:
        """Get a list of all unique categories."""
        return list(set(t.category for t in self.templates.values()))
    
    def list_subcategories(self, category: Optional[str] = None) -> List[str]:
        """Get a list of all unique subcategories."""
        templates = self.templates.values()
        
        if category:
            templates = [t for t in templates if t.category == category]
            
        return list(set(t.subcategory for t in templates if t.subcategory))
    
    def load_default_templates(self) -> None:
        """Load the default templates."""
        from .default_templates import DEFAULT_TEMPLATES
        
        for template_data in DEFAULT_TEMPLATES:
            try:
                template = Template.from_dict(template_data)
                self.add_template(template)
            except ValueError as e:
                # If template with same ID already exists, skip it
                pass