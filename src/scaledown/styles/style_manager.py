from typing import Dict, List, Optional

from .style import Style
from .default_styles import DEFAULT_STYLES, create_expert_style, EXPERT_DOMAINS, EXPERT_ROLES

class StyleManager:
    """Manager for style operations."""
    
    def __init__(self):
        """Initialize style manager."""
        self.styles: Dict[str, Style] = {}
    
    def add_style(self, style: Style) -> None:
        """Add a style to the manager."""
        if style.id in self.styles:
            raise ValueError(f"Style with ID '{style.id}' already exists")
        
        self.styles[style.id] = style
    
    def get_style(self, style_id: str) -> Optional[Style]:
        """Get a style by ID."""
        return self.styles.get(style_id)
    
    def list_styles(self) -> List[Style]:
        """List all available styles."""
        return list(self.styles.values())
    
    def load_default_styles(self) -> None:
        """Load the default styles."""
        for style_data in DEFAULT_STYLES:
            try:
                style = Style.from_dict(style_data)
                self.add_style(style)
            except ValueError:
                # Skip if style with same ID already exists
                pass
    
    def create_expert_style(self, domain: str, role: str, expertise_level: int = 85) -> Style:
        """Create and register a custom expert style."""
        if domain not in EXPERT_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}. Choose from: {', '.join(EXPERT_DOMAINS)}")
        
        if role not in EXPERT_ROLES:
            raise ValueError(f"Invalid role: {role}. Choose from: {', '.join(EXPERT_ROLES)}")
        
        style_data = create_expert_style(domain, role, expertise_level)
        style = Style.from_dict(style_data)
        
        # Add to manager
        try:
            self.add_style(style)
        except ValueError:
            # Replace if it already exists
            self.styles[style.id] = style
            
        return style