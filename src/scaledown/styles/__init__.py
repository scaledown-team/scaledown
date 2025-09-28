from .style import Style
from .style_manager import StyleManager
from .default_styles import DEFAULT_STYLES, EXPERT_DOMAINS, EXPERT_ROLES
from .optimization_style import (
    OptimizationStyle,
    create_default_optimization_styles,
    get_optimization_style_by_optimizers
)

def get_default_style_manager() -> StyleManager:
    """Get a style manager pre-loaded with default styles."""
    manager = StyleManager()
    manager.load_default_styles()
    return manager

def get_enhanced_style_manager() -> StyleManager:
    """Get a style manager with both default and optimization styles."""
    manager = StyleManager()
    manager.load_default_styles()

    # Add optimization styles
    optimization_styles = create_default_optimization_styles()
    for style in optimization_styles:
        manager.add_style(style)

    return manager

__all__ = [
    'Style',
    'StyleManager',
    'DEFAULT_STYLES',
    'EXPERT_DOMAINS',
    'EXPERT_ROLES',
    'OptimizationStyle',
    'create_default_optimization_styles',
    'get_optimization_style_by_optimizers',
    'get_default_style_manager',
    'get_enhanced_style_manager'
]