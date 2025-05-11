import re
from typing import List, Dict, Any, Optional

class Template:
    """Base class for all prompt templates."""
    
    def __init__(self, id, title, template_text, category, subcategory=None, metadata=None):
        self.id = id
        self.title = title
        self.template_text = template_text
        self.category = category
        self.subcategory = subcategory
        self.metadata = metadata or {}
        self.placeholders = self._extract_placeholders()
    
    def _extract_placeholders(self) -> List[str]:
        """Extract all placeholders from the template text."""
        return re.findall(r'\[(.*?)\]', self.template_text)
    
    def render(self, **kwargs):
        """Render the template with provided values."""
        filled_template = self.template_text
        
        # Check for missing required placeholders
        missing = [p for p in self.placeholders if p not in kwargs]
        if missing:
            raise ValueError(f"Missing required placeholders: {', '.join(missing)}")
        
        # Replace placeholders with values
        for placeholder, value in kwargs.items():
            if placeholder in self.placeholders:
                filled_template = filled_template.replace(f"[{placeholder}]", str(value))
        
        return filled_template
    
    def to_dict(self):
        """Convert template to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "template": self.template_text,
            "category": self.category,
            "subcategory": self.subcategory,
            "metadata": self.metadata,
            "placeholders": self.placeholders
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a template from a dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("title"),
            template_text=data.get("template"),
            category=data.get("category"),
            subcategory=data.get("subcategory"),
            metadata=data.get("metadata", {})
        )