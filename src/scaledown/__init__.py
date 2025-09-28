from .templates import Template, TemplateManager, get_default_manager as get_default_template_manager
from .styles import (
    Style, StyleManager, get_default_style_manager, get_enhanced_style_manager,
    OptimizationStyle
)
from .api import ScaleDown

# Import optimization components
try:
    from .optimization import (
        optimize_prompt, parse_optimizers, OPTIMIZER_PROMPTS,
        get_optimizer_registry, PromptOptimizerRegistry
    )
    _optimization_available = True
except ImportError:
    _optimization_available = False

# Import tools for backward compatibility
try:
    from .tools import tools, LLMProviderFactory
    _tools_available = True
except ImportError:
    _tools_available = False

# Create a singleton instance for easy access with optimization enabled
sd = ScaleDown(enable_optimization_styles=True)

# Export main classes
__all__ = [
    'Template',
    'TemplateManager',
    'Style',
    'StyleManager',
    'OptimizationStyle',
    'ScaleDown',
    'sd',
    'get_default_template_manager',
    'get_default_style_manager',
    'get_enhanced_style_manager'
]

# Add optimization exports if available
if _optimization_available:
    __all__.extend([
        'optimize_prompt',
        'parse_optimizers',
        'OPTIMIZER_PROMPTS',
        'get_optimizer_registry',
        'PromptOptimizerRegistry'
    ])

# Add tools exports if available
if _tools_available:
    __all__.extend([
        'tools',
        'LLMProviderFactory'
    ])

# Version info
__version__ = "0.2.0"