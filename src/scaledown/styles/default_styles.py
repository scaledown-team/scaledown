DEFAULT_STYLES = [
    {
        "id": "standard",
        "name": "Standard",
        "description": "Direct instructions with clear objectives",
        "icon": "pencil",
        "template_modifier": "",
        "system_prompt": "Provide clear, direct responses that address the question efficiently."
    },
    {
        "id": "chain_of_thought",
        "name": "Chain of Thought",
        "description": "Guides the AI to show its reasoning process step-by-step",
        "icon": "gear",
        "template_modifier": "Think through this step-by-step: ",
        "system_prompt": "Walk through your reasoning process step-by-step before providing your final answer."
    },
    {
        "id": "concise",
        "name": "Concise",
        "description": "Brief, to-the-point responses with minimal explanation",
        "icon": "arrow",
        "template_modifier": "Be concise: ",
        "system_prompt": "Provide brief, to-the-point responses with minimal explanation."
    },
    {
        "id": "detailed",
        "name": "Detailed",
        "description": "Comprehensive responses with thorough explanations",
        "icon": "chat",
        "template_modifier": "Explain in detail: ",
        "system_prompt": "Provide comprehensive responses with thorough explanations."
    },
    {
        "id": "creative",
        "name": "Creative",
        "description": "Encourages innovative and unconventional thinking",
        "icon": "gear",
        "template_modifier": "Think creatively: ",
        "system_prompt": "Approach this with innovative and unconventional thinking."
    }
]

# Expert mode configuration options
EXPERT_DOMAINS = [
    "Technology", "Business", "Science", "Health", "Education", 
    "Finance", "Law", "Engineering", "Marketing", "Design"
]

EXPERT_ROLES = [
    "Consultant", "Analyst", "Researcher", "Developer", "Strategist",
    "Manager", "Educator", "Advisor", "Engineer", "Designer"
]

def create_expert_style(domain, role, expertise_level=85):
    """Create an expert style with specific domain and role."""
    level_text = "Knowledgeable"
    if expertise_level > 90:
        level_text = "World-Class"
    elif expertise_level > 70:
        level_text = "Highly Experienced"
    
    return {
        "id": f"expert_{domain.lower()}_{role.lower()}",
        "name": f"{domain} {role}",
        "description": f"Expert {role} in {domain} with {level_text} expertise",
        "icon": "person-gear",
        "template_modifier": f"As an expert {domain} {role}: ",
        "system_prompt": f"You are an {expertise_level}th percentile {domain} {role}. Provide expert-level advice and insights based on your specialized knowledge."
    }