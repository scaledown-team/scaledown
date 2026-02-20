
"""
Google Gemini API Client.
"""
import requests
import json
from typing import List, Dict, Generator, Any

from pulse.exceptions import InferenceError

class GeminiClient:
    """
    Client for Google's Gemini API via REST.
    """
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        if not self.model.startswith("models/"):
            self.model = f"models/{model}"
            
    @property
    def default_model(self) -> str:
        return self.model
        
    @default_model.setter
    def default_model(self, value: str):
        self.model = value
            
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat message to Gemini using specified curl-like structure.
        """
        # Clean model name if it has prefixes
        model_name = self.model.replace("models/", "")
        url = f"{self.BASE_URL}/models/{model_name}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        
        contents = self._prepare_contents(messages)
        system_instruction = self._extract_system_instruction(messages)
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 8192)
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        # Retry logic for 429 (Quota) or 503 (Overloaded)
        import time
        max_retries = 3
        backoff = 2
        
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    break # Success
                    
                if response.status_code in [429, 503]:
                    print(f"Gemini API rate limit (429). Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                
                # If other error, raise immediately
                raise InferenceError(f"Gemini API Error {response.status_code}: {response.text}")
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise InferenceError(f"Network error after {max_retries} attempts: {str(e)}")
                time.sleep(backoff)
                continue
        
        if not response:
             raise InferenceError("No response received from Gemini API.")
             
        if response.status_code != 200:
             raise InferenceError(f"Gemini API Error {response.status_code}: {response.text}")

        data = response.json()
        try:
            # Handle cases where content might be blocked or empty
            if 'candidates' not in data or not data['candidates']:
                raise InferenceError("No candidates returned (possibly blocked).")
                
            candidate = data['candidates'][0]
            if 'content' not in candidate:
                    finish_reason = candidate.get('finishReason', 'UNKNOWN')
                    raise InferenceError(f"Response blocked. Reason: {finish_reason}")
                    
            text = candidate['content']['parts'][0]['text']
            usage = data.get("usageMetadata", {})
            
            return {
                "content": text,
                "model": self.model,
                "usage": usage
            }
        except (KeyError, IndexError) as e:
                raise InferenceError(f"Unexpected response format: {str(e)}")

    def stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        Stream chat response.
        """
        model_name = self.model.replace("models/", "")
        url = f"{self.BASE_URL}/models/{model_name}:streamGenerateContent?alt=sse"
        
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        
        contents = self._prepare_contents(messages)
        system_instruction = self._extract_system_instruction(messages)
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 8192)
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            
        try:
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
            
            if response.status_code != 200:
                 raise InferenceError(f"Stream Error {response.status_code}: {response.text}")
                 
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        json_str = decoded[6:]
                        try:
                            chunk = json.loads(json_str)
                            if 'candidates' in chunk and chunk['candidates']:
                                parts = chunk['candidates'][0].get('content', {}).get('parts', [])
                                if parts:
                                    text = parts[0].get('text', '')
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            raise InferenceError(f"Stream error: {str(e)}")

    def _extract_system_instruction(self, messages: List[Dict[str, str]]) -> str:
        """Extract system prompt."""
        for msg in messages:
            if msg["role"] == "system":
                return msg["content"]
        return ""

    def _prepare_contents(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Map messages to Gemini role/parts structure."""
        contents = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                continue # Handled separately
            
            mapped_role = "user" if role == "user" else "model"
            contents.append({
                "role": mapped_role,
                "parts": [{"text": content}]
            })
        return contents
