"""
Client for OpenRouter API.
"""

import json
import requests
from typing import List, Dict, Generator, Any

from pulse.exceptions import InferenceError


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API.
    Handles authentication, model selection, and fallback logic.
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str, default_model: str, fallback_models: List[str] = None):
        self.api_key = api_key
        self.default_model = default_model
        self.fallback_models = fallback_models or []
        self._available_models = None
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pulse-ai.local",  # Required by OpenRouter for stats
            "X-Title": "Pulse AI Ecosystem"
        }

    @staticmethod
    def _normalize_model_id(model_id: str) -> str:
        """Normalize common model-id formatting issues."""
        if not model_id:
            return model_id
        normalized = model_id.strip()
        while "::" in normalized:
            normalized = normalized.replace("::", ":")
        normalized = normalized.replace("-02-055:free", "-02-05:free")
        return normalized

    def _get_available_models(self) -> set:
        """Fetch available model IDs once and cache them."""
        if self._available_models is not None:
            return self._available_models

        try:
            response = requests.get(
                f"{self.BASE_URL}/models",
                headers=self.headers,
                timeout=20
            )
            if response.status_code != 200:
                self._available_models = set()
                return self._available_models

            data = response.json().get("data", [])
            self._available_models = {
                item.get("id", "") for item in data if item.get("id")
            }
        except Exception:
            self._available_models = set()

        return self._available_models

    def _build_models_to_try(self, model: str = None) -> List[str]:
        """Build normalized, deduplicated, and availability-filtered model list."""
        target_model = self._normalize_model_id(model or self.default_model)
        configured = [target_model] + [self._normalize_model_id(m) for m in self.fallback_models]

        deduped = []
        seen = set()
        for model_id in configured:
            if model_id and model_id not in seen:
                deduped.append(model_id)
                seen.add(model_id)

        available = self._get_available_models()
        if not available:
            return deduped

        filtered = [m for m in deduped if m in available]

        # If everything configured is unavailable, choose stable free models from catalog.
        if not filtered:
            free_models = sorted([m for m in available if m.endswith(":free")])
            return free_models[:3] if free_models else deduped

        return filtered

    def chat(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request with robust fallback.
        """
        models_to_try = self._build_models_to_try(model)
        target_model = models_to_try[0] if models_to_try else self._normalize_model_id(model or self.default_model)

        last_error = None
        for m in models_to_try:
            try:
                # If we are retrying, print a friendly message
                if m != target_model:
                    print(f"⚠️ Primary model rate-limited/failed. Retrying with: {m}...")
                
                return self._make_request(m, messages, **kwargs)
                
            except InferenceError as e:
                last_error = e
                error_str = str(e).lower()
                print(f"❌ Error with model {m}: {e}")
                
                # Dynamic Self-Healing:
                # Retry on:
                # 1. 429 Rate Limits (temporarily busy)
                # 2. 400/404 Invalid Model (model deprecated or ID changed)
                # 3. 5xx Server Errors (upstream outage)
                should_retry = False
                for indicator in ["429", "rate limit", "temporarily", "400", "404", "not a valid model", "not found"]:
                    if indicator in error_str:
                        should_retry = True
                        break
                
                if should_retry:
                    continue  # Try next model
                else:
                    raise e  # Re-raise other errors (e.g. auth, context length)
        
        # If we exhausted all options
        raise InferenceError(f"All models failed. Last error: {last_error}")

    def _make_request(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Internal method to execute the API call."""
        payload = {
            "model": model,
            "messages": messages,
        }
        
        # Add optional parameters like 'temperature', 'max_tokens', etc.
        # Filter out 'reasoning' as it's not widely supported and can cause issues
        for key, value in kwargs.items():
            if key != 'reasoning':  # Skip reasoning parameter
                payload[key] = value
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # Check for error responses that are valid JSON but contain error info
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    raise InferenceError(f"API Error {response.status_code}: {error_msg}")
                except json.JSONDecodeError:
                    raise InferenceError(f"HTTP Error {response.status_code}: {response.text}")
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise InferenceError("Invalid API response: no choices found")
                
            choice = data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            reasoning_details = message.get("reasoning_details")
            
            return {
                "content": content,
                "model": data.get("model", model),
                "usage": data.get("usage", {}),
                "reasoning_details": reasoning_details
            }
            
        except requests.exceptions.Timeout:
             raise InferenceError(f"Request timed out for model {model}")
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Network error: {str(e)}")

    def stream(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Generator[str, None, None]:
        """
        Stream chat completion chunks with robust fallback.
        """
        models_to_try = self._build_models_to_try(model)
        target_model = models_to_try[0] if models_to_try else self._normalize_model_id(model or self.default_model)
        
        last_error = None
        
        for m in models_to_try:
            try:
                if m != target_model:
                     # Yield a system notice if we are switching models mid-stream context
                     # (Though we can't easily yield a 'system notice' as text content without confusing the user, 
                     # we'll just log it for now)
                     print(f"⚠️ Streaming fallback: switching to {m}...")

                # Create the generator
                stream_generator = self._make_stream_request(m, messages, **kwargs)
                
                # Yield from the generator
                # If this raises an exception immediately, we catch it below.
                # If it raises halfway through, the stream breaks (hard to recover mid-stream), 
                # but at least initial connection is protected.
                yield from stream_generator
                return

            except InferenceError as e:
                last_error = e
                error_str = str(e).lower()
                
                # Dynamic Self-Healing for Streams:
                # Catch 429 (Rate Limit), 400 (Invalid Model), 404 (Not Found)
                should_retry = False
                for indicator in ["429", "rate limit", "temporarily", "400", "404", "not a valid model", "not found"]:
                    if indicator in error_str:
                        should_retry = True
                        break

                if should_retry:
                    continue
                else:
                    raise e
                    
        raise InferenceError(f"All streaming models failed. Last error: {last_error}")

    def _make_stream_request(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Internal method for streaming request."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                # Try to get error text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', response.text)
                except ValueError:
                    error_msg = response.text
                raise InferenceError(f"API Error {response.status_code}: {error_msg}")
                
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Stream network error: {str(e)}")
