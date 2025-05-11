# optimization/token_optimizer.py
from typing import List, Tuple, Set, Dict

class TokenOptimizer:
    """Optimizes prompts by reducing token count while preserving meaning."""
    
    def __init__(self):
        # Common filler words that can often be removed
        self.filler_words = {
            "please", "kindly", "just", "basically", "actually", "really",
            "very", "quite", "simply", "just", "that is", "I mean",
            "you know", "like", "so", "well", "you see", "kind of",
            "sort of", "I guess", "I suppose", "I would say",
            "as a matter of fact", "needless to say", "as you may know"
        }
        
        # Phrases that can be simplified
        self.simplifications = {
            "due to the fact that": "because",
            "in order to": "to",
            "for the purpose of": "for",
            "in the event that": "if",
            "in the process of": "while",
            "on the occasion of": "when",
            "in spite of the fact that": "although",
            "with reference to": "about",
            "with regard to": "about",
            "it is important to note that": "",
            "it should be noted that": "",
            "it is worth noting that": "",
            "it is important to remember that": "",
            "it is crucial to understand that": "",
            "if you don't mind": "",
            "if it's not too much trouble": "",
            "I was wondering if you could": "",
            "I would like you to": "",
            "could you please": "",
        }
    
    def optimize(self, text: str) -> str:
        """Optimize text to reduce token count.
        
        Args:
            text: Original text to optimize
            
        Returns:
            Optimized text
        """
        result = text
        
        # Remove unnecessary filler words
        for word in self.filler_words:
            result = result.replace(f" {word} ", " ")
        
        # Apply simplifications
        for phrase, replacement in self.simplifications.items():
            result = result.replace(phrase, replacement)
        
        # Remove double spaces
        while "  " in result:
            result = result.replace("  ", " ")
        
        return result.strip()