from .template import Template
from .template_manager import TemplateManager
from .default_templates import DEFAULT_TEMPLATES

def get_default_manager() -> TemplateManager:
    """Get a template manager pre-loaded with default templates."""
    manager = TemplateManager()
    manager.load_default_templates()
    return manager