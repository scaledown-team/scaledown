from typing import List
from .prompts import (
    EXPERT_PERSONA_PROMPT,
    UNCERTAINTY_PROMPT,
    COT_PROMPT,
    COVE_PROMPT,
)


OPTIMIZER_PROMPTS = {
    "expert_persona": EXPERT_PERSONA_PROMPT,
    "cot": COT_PROMPT, 
    "uncertainty": UNCERTAINTY_PROMPT,
    "cove": COVE_PROMPT,
    "none": "",  # Baseline prompt without optimization
}


def parse_optimizers(optimizers_string: str) -> List[str]:
    """Parse comma-separated optimizer string into list of optimizer names."""
    if not optimizers_string:
        return []
    
    optimizers = [opt.strip() for opt in optimizers_string.split(",")]
    
    # Validate all optimizers exist
    invalid_optimizers = [opt for opt in optimizers if opt not in OPTIMIZER_PROMPTS]
    if invalid_optimizers:
        valid_opts = ", ".join(OPTIMIZER_PROMPTS.keys())
        raise ValueError(f"Invalid optimizers: {invalid_optimizers}. Valid options: {valid_opts}")
    
    return optimizers


def optimize_prompt(question: str, optimizers_list: List[str]) -> str:
    """
    Build optimized prompt by applying the specified optimizers to a question.

    Args:
        question: The question to optimize
        optimizers_list: List of optimizer names to apply (can be empty)

    Returns:
        Optimized prompt with applied optimizers
    """
    prompt_parts = []

    # 1. ROLE (if expert_persona in optimizers)
    if optimizers_list and "expert_persona" in optimizers_list:
        prompt_parts.append(EXPERT_PERSONA_PROMPT)

    # 2. Add other optimizers in user-specified order
    if optimizers_list:
        for optimizer_name in optimizers_list:
            if optimizer_name in ["expert_persona", "none"]:
                continue
            optimizer_prompt = OPTIMIZER_PROMPTS.get(optimizer_name)
            if optimizer_prompt:
                prompt_parts.append(optimizer_prompt)

    # 3. Add the question
    prompt_parts.append(question)

    return "\n\n".join(prompt_parts)

