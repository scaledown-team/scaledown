from .llms import LLMProviderFactory
from .prompt_optimizer import optimize_prompt, parse_optimizers, OPTIMIZER_PROMPTS

def tools(llm='', optimiser=''):
    """
    Main entry point for ScaleDown tools.
    
    Args:
        llm (str): LLM model identifier (e.g., 'gemini-1.5-flash', 'scaledown-gpt-4o')
        optimiser (str): Optimizer strategy (e.g., 'expert_persona', 'cot', 'uncertainty', 'cove')
    
    Returns:
        dict: Dictionary containing llm_provider and optimizer configuration
    
    Example:
        >>> from scaledown.tools import tools
        >>> result = tools(llm='gemini-1.5-flash', optimiser='cot')
        >>> llm_provider = result['llm_provider']
        >>> optimizer = result['optimizer']
    """
    result = {}
    
    if llm:
        try:
            llm_provider = LLMProviderFactory.create_provider(llm)
            result['llm_provider'] = llm_provider
        except Exception as e:
            result['llm_error'] = str(e)
    
    if optimiser:
        try:
            optimizer_list = parse_optimizers(optimiser)
            result['optimizer'] = optimizer_list
            result['optimizer_prompts'] = {opt: OPTIMIZER_PROMPTS[opt] for opt in optimizer_list}
        except Exception as e:
            result['optimizer_error'] = str(e)
    
    return result

__all__ = ['tools', 'LLMProviderFactory', 'optimize_prompt', 'parse_optimizers', 'OPTIMIZER_PROMPTS']