"""
The Brain: Central Orchestrator for Pulse Ecosystem.
Integrates Memory, ScaleDown, and OpenRouter.
"""

import time
import re
from typing import List, Dict, Generator, Union

try:
    from scaledown import ScaleDownCompressor
    from scaledown.exceptions import APIError as ScaleDownAPIError
except ImportError:
    ScaleDownCompressor = None
    ScaleDownAPIError = None

from pulse.config import PulseConfig
from pulse.core.memory import Memory
from pulse.core.openrouter_client import OpenRouterClient
from pulse.exceptions import ConfigurationError, ContextOptimizationError, InferenceError


class Brain:
    """
    The intelligence core of Pulse.
    
    Responsibility:
    1. Manage conversation state via Memory.
    2. Optimize context usage via ScaleDown.
    3. Generate responses via OpenRouter.
    """
    
    def __init__(self, config: PulseConfig):
        self.config = config
        
        # Initialize components
        self.memory = Memory(config.db_path, config.encryption_key)
        
        self.llm = OpenRouterClient(
            api_key=config.openrouter_api_key,
            default_model=config.default_model,
            fallback_models=config.fallback_models
        )
        
        # Initialize ScaleDown if API key is present
        self.compressor = None
        if config.scaledown_api_key and ScaleDownCompressor:
            import scaledown as sd
            sd.set_api_key(config.scaledown_api_key)
            self.compressor = ScaleDownCompressor(
                target_model="gpt-4o",  # ScaleDown target model for compression
                rate=config.compression_rate
            )
        else:
             print("Warning: ScaleDown module not found or disabled. Context optimization will be skipped.")
            
        # Skill Registry
        from pulse.skills.system_skills import TimeSkill, SystemInfoSkill
        self.skills = [TimeSkill(), SystemInfoSkill()]

    
    def think(self, user_input: str, system_prompt: str = None) -> str:
        """
        Process user input and return a response (synchronous).
        """
        # 1. Add user message to memory
        self.memory.add("user", user_input)

        # 2. Check skills first for deterministic local answers
        skill_result, skill_name = self._run_skill_if_matched(user_input)
        if skill_result is not None:
            self.memory.add("assistant", skill_result, metadata={"skill": skill_name})
            return skill_result
        
        # 3. Prepare context
        context_messages = self._prepare_context(system_prompt)

        # 4. Call LLM with controlled temperature to reduce hallucinations
        start_time = time.time()
        # Use lower temperature for more focused, accurate responses
        result = self.llm.chat(context_messages, temperature=0.3, max_tokens=1000)
        latency = (time.time() - start_time) * 1000
        
        response_content = result["content"]
        
        # 4. Save response to memory
        metadata = {
            "model": result.get("model"),
            "latency_ms": latency,
            "usage": result.get("usage"),
            "reasoning_details": result.get("reasoning_details")
        }
        self.memory.add("assistant", response_content, metadata)
        
        return response_content

    def stream_thought(self, user_input: str, system_prompt: str = None) -> Generator[str, None, None]:
        """
        Stream the thought process (response).
        """
        self.memory.add("user", user_input)

        skill_result, skill_name = self._run_skill_if_matched(user_input)
        if skill_result is not None:
            self.memory.add("assistant", skill_result, metadata={"skill": skill_name})
            yield skill_result
            return

        context_messages = self._prepare_context(system_prompt)
        
        full_response = []
        
        try:
            for chunk in self.llm.stream(context_messages, temperature=0.3, max_tokens=1000):
                full_response.append(chunk)
                yield chunk
        finally:
            # Save full response even if interrupted
            content = "".join(full_response)
            if content and len(content.strip()) > 0:
                self.memory.add("assistant", content)

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()

    def _skill_by_name(self, name: str):
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

    @staticmethod
    def _contains_any(text: str, terms: List[str]) -> bool:
        return any(term in text for term in terms)

    def _run_skill_if_matched(self, user_input: str):
        normalized_input = self._normalize_text(user_input)

        for skill in self.skills:
            for cmd in skill.commands:
                normalized_cmd = self._normalize_text(cmd)
                if normalized_cmd and normalized_cmd in normalized_input:
                    print(f"Executing Skill: {skill.name}")
                    return skill.execute({"user_input": user_input}), skill.name

        # Heuristic fallback for natural phrasing that may not exactly match commands
        if self._contains_any(normalized_input, ["time", "date", "today"]):
            skill = self._skill_by_name("time")
            if skill:
                print(f"Executing Skill: {skill.name}")
                return skill.execute({"user_input": user_input}), skill.name

        if self._contains_any(normalized_input, ["cpu", "ram", "memory", "system status", "system info"]):
            skill = self._skill_by_name("system_info")
            if skill:
                print(f"Executing Skill: {skill.name}")
                return skill.execute({"user_input": user_input}), skill.name

        return None, None

    def _prepare_context(self, system_prompt: str = None) -> List[Dict[str, str]]:
        """
        Prepare and optimize context for the LLM.
        """
        # Get recent history
        # Keep context focused with fewer messages to reduce hallucinations
        raw_history = self.memory.get_history(limit=10)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are Groot, an intelligent and helpful AI assistant. Respond directly and clearly to user questions with accurate, relevant information. Always provide complete answers in English. Stay focused on the user's question and avoid tangential or irrelevant information. Be concise but thorough."})
        
        # If optimization is disabled or we don't have enough history, return as is
        if not self.config.enable_context_optimization or len(raw_history) < 6 or not self.compressor:
            # Limit to last 8 messages maximum to prevent confusion
            limited_history = raw_history[-8:] if len(raw_history) > 8 else raw_history
            for msg in limited_history:
                messages.append({"role": msg.role, "content": msg.content})
            return messages
        
        # --- Context Optimization Logic ---
        # Strategy: Keep last 3 turns (6 messages) raw, compress older history
        
        recent_turns = raw_history[-6:] 
        older_turns = raw_history[:-6]
        
        # Convert older turns to a single text block for compression
        older_context_str = "\n".join([f"{m.role.upper()}: {m.content}" for m in older_turns])
        
        # Create a "pseudo-prompt" for the compressor to know what's relevant to the recent conversation
        # Using the last user message as the anchor
        current_query = raw_history[-1].content
        
        try:
            # Compress older context
            compressed = self.compressor.compress(
                context=older_context_str,
                prompt=current_query
            )
            
            # Add compressed summary as a system note or distinct message
            messages.append({
                "role": "system", 
                "content": f"Prior Conversation Summary (Optimized): {compressed.content}"
            })
            
        except Exception as e:
            # Fallback to raw if compression fails
            print(f"Warning: Context optimization failed ({e}), using raw history.")
            for msg in older_turns:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Append recent raw messages
        for msg in recent_turns:
            messages.append({"role": msg.role, "content": msg.content})
            
        return messages

    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()
