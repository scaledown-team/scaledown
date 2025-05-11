from .style import Style
from .style_manager import StyleManager
from .default_styles import DEFAULT_STYLES, EXPERT_DOMAINS, EXPERT_ROLES

def get_default_style_manager() -> StyleManager:
    """Get a style manager pre-loaded with default styles."""
    manager = StyleManager()
    manager.load_default_styles()
    return manager