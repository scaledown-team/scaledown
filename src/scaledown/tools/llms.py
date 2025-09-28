import time
import sys
import requests
import json
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LLMProviderFactory:
    """Simple LLM provider that auto-detects based on model name."""
    
    @staticmethod
    def create_provider(model_id: str, temperature: float = 0.0, configuration: Dict[str, str] = None) -> 'LLM':
        """Create LLM provider based on model name."""
        if configuration is None:
            configuration = {}
            
        if "gemini" in model_id.lower():
            return GoogleLLM(model_id, temperature, configuration)
        elif "scaledown" in model_id.lower() or "gpt" in model_id.lower():
            return ScaledownLLM(model_id, temperature, configuration)
        else:
            raise ValueError(f"Unsupported model: {model_id}")


class LLM:
    """Base LLM interface."""
    
    def __init__(self, model_id: str, temperature: float, configuration: Dict[str, str]):
        self.model_id = model_id
        self.temperature = temperature
        self.configuration = configuration
        self.configure()
    
    def configure(self):
        """Configure the provider."""
        pass
    
    def call_llm(self, prompt: str, max_tokens: int) -> str:
        """Call the LLM."""
        raise NotImplementedError
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'model_id': self.model_id,
            'temperature': self.temperature,
            'provider': self.__class__.__name__
        }


class GoogleLLM(LLM):
    """Google Gemini LLM."""
    
    def configure(self):
        if genai is None:
            raise ImportError("google-generativeai not installed")
            
        api_key = self.configuration.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in configuration")
        
        genai.configure(api_key=api_key)
        
        # Map model names to correct Google model IDs
        model_mapping = {
            "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-1.5-pro": "gemini-1.5-pro"
        }
        actual_model = model_mapping.get(self.model_id, self.model_id)
        
        self.model = genai.GenerativeModel(actual_model)
        self.last_request_time = 0
        self.min_request_interval = 4.0  # Rate limiting
    
    def call_llm(self, prompt: str, max_tokens: int) -> str:
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                return "No response generated"
                
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                print(f"\n❌ API quota exceeded: {e}")
                sys.exit(1)
            else:
                raise e


class ScaledownLLM(LLM):
    """Scaledown API LLM."""
    
    def configure(self):
        api_key = self.configuration.get("SCALEDOWN_API_KEY")
        if not api_key:
            raise ValueError("SCALEDOWN_API_KEY not found in configuration")
        
        self.api_key = api_key
        self.endpoint = "https://api.scaledown.xyz/compress"
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Map model names to actual model IDs
        if self.model_id == "scaledown-gpt-4o":
            self.actual_model = "gpt-4o"
        else:
            self.actual_model = self.model_id
        
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Basic rate limiting
    
    def call_llm(self, prompt: str, max_tokens: int) -> str:
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        
        payload = {
            "context": "",
            "prompt": prompt,
            "model": self.actual_model,
            "scaledown": {
                "rate": 0.0
            }
        }
        
        if self.temperature > 0:
            payload["temperature"] = self.temperature
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if "full_response" in result:
                    return result["full_response"].strip()
                elif "response" in result:
                    return result["response"].strip()
                elif "text" in result:
                    return result["text"].strip()
                elif "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return str(result).strip()
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                raise RuntimeError(f"Scaledown API request failed: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Scaledown API request failed: {e}")