from .llms import LLMProviderFactory
from .prompt_optimizer import optimize_prompt, parse_optimizers, OPTIMIZER_PROMPTS

def tools(llm='', optimiser='', enable_enhanced_features=False):
    """
    Main entry point for ScaleDown tools with backward compatibility.

    Args:
        llm (str): LLM model identifier (e.g., 'gemini-1.5-flash', 'scaledown-gpt-4o')
        optimiser (str): Optimizer strategy (e.g., 'expert_persona', 'cot', 'uncertainty', 'cove')
        enable_enhanced_features (bool): Enable enhanced ScaleDown integration features

    Returns:
        dict: Dictionary containing llm_provider and optimizer configuration

    Example:
        >>> from scaledown.tools import tools
        >>> result = tools(llm='gemini-1.5-flash', optimiser='cot')
        >>> llm_provider = result['llm_provider']
        >>> optimizer = result['optimizer']

        # Enhanced usage with full ScaleDown integration
        >>> result = tools(llm='scaledown-gpt-4o', optimiser='expert_persona,cot', enable_enhanced_features=True)
        >>> scaledown_instance = result['scaledown']
        >>> model = result['llm_model']
    """
    result = {}

    # Legacy LLM provider support
    if llm:
        try:
            llm_provider = LLMProviderFactory.create_provider(llm)
            result['llm_provider'] = llm_provider

            # Enhanced model integration if requested
            if enable_enhanced_features:
                try:
                    from ..models.llm_model import LLMModelFactory
                    llm_model = LLMModelFactory.create_model(llm)
                    result['llm_model'] = llm_model
                except ImportError:
                    pass

        except Exception as e:
            result['llm_error'] = str(e)

    # Optimizer support
    if optimiser:
        try:
            optimizer_list = parse_optimizers(optimiser)
            result['optimizer'] = optimizer_list
            result['optimizer_prompts'] = {opt: OPTIMIZER_PROMPTS[opt] for opt in optimizer_list}

            # Enhanced optimization features if requested
            if enable_enhanced_features:
                try:
                    from ..optimization.prompt_optimizers import get_optimizer_registry
                    registry = get_optimizer_registry()
                    result['optimizer_registry'] = registry
                    result['optimizer_info'] = [
                        registry.get_optimizer_info(opt) for opt in optimizer_list
                        if registry.get_optimizer_info(opt)
                    ]

                    # Create optimization style if possible
                    from ..styles.optimization_style import get_optimization_style_by_optimizers
                    optimization_style = get_optimization_style_by_optimizers(optimizer_list)
                    if optimization_style:
                        result['optimization_style'] = optimization_style

                except ImportError:
                    pass

        except Exception as e:
            result['optimizer_error'] = str(e)

    # Enhanced ScaleDown integration
    if enable_enhanced_features:
        try:
            from ..api import ScaleDown
            scaledown_instance = ScaleDown(enable_optimization_styles=True)

            # Pre-configure if model and optimizers provided
            if llm:
                scaledown_instance.select_model(llm)
            if optimiser:
                scaledown_instance.select_optimization_style(optimizer_list)

            result['scaledown'] = scaledown_instance
            result['enhanced_features_enabled'] = True

        except ImportError:
            result['enhanced_features_available'] = False

    return result

__all__ = ['tools', 'LLMProviderFactory', 'optimize_prompt', 'parse_optimizers', 'OPTIMIZER_PROMPTS']