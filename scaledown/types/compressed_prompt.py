from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class CompressedPrompt:
    content: str
    original_prompt: str
    tokens: Tuple[int, int]  # (original, compressed)
    latency: float
    target_model: str
    
    @property
    def compression_ratio(self) -> float:
        if self.tokens[1] == 0: return 0.0
        return self.tokens[0] / self.tokens[1]

    @property
    def savings_percent(self) -> float:
        if self.tokens[0] == 0: return 0.0
        return (1 - (self.tokens[1] / self.tokens[0])) * 100

    @classmethod
    def from_api_response(cls, content: str, raw_response: Dict[str, Any]) -> "CompressedPrompt":
        """Factory method to create instance from raw API response dict."""
        return cls(
            content=content,
            original_prompt=raw_response.get("original_prompt", ""),
            tokens=(
                raw_response.get("original_prompt_tokens", 0),
                raw_response.get("compressed_prompt_tokens", 0)
            ),
            latency=raw_response.get("latency_ms", 0.0),
            model=raw_response.get("model_used", "unknown")
        )
