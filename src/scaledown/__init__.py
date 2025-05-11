from .templates import Template, TemplateManager, get_default_manager as get_default_template_manager
from .styles import Style, StyleManager, get_default_style_manager
from .api import ScaleDown

# Create a singleton instance for easy access
sd = ScaleDown()

# Export main classes
__all__ = [
    'Template', 
    'TemplateManager', 
    'Style',
    'StyleManager',
    'ScaleDown',
    'sd'
]