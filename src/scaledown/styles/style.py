class Style:
    """Class representing a response style for AI models."""
    
    def __init__(self, id, name, description, icon="default", 
                 template_modifier="", system_prompt=""):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.template_modifier = template_modifier
        self.system_prompt = system_prompt
    
    def apply_to_prompt(self, prompt_text):
        """Apply this style to a prompt text."""
        if self.template_modifier:
            return f"{self.template_modifier}{prompt_text}"
        return prompt_text
    
    def to_dict(self):
        """Convert style to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "template_modifier": self.template_modifier,
            "system_prompt": self.system_prompt
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a style from a dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            icon=data.get("icon", "default"),
            template_modifier=data.get("template_modifier", ""),
            system_prompt=data.get("system_prompt", "")
        )