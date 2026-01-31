import pytest 
import os
from unittest.mock import patch, MagicMock
import scaledown as sd

@pytest.fixture
def compressor():
    return sd.ScaleDownCompressor(api_key="test_key")

def test_missing_api_key(monkeypatch):
    """Test that initialization fails if no API key is found anywhere."""
    monkeypatch.delenv("SCALEDOWN_API_KEY", raising=False)
    sd.set_api_key(None)  # Ensure no API key is set globally
    
    # Don't pass api_key - should fail since no key is available
    comp = sd.ScaleDownCompressor()
    
    with pytest.raises(sd.AuthenticationError):
        comp.compress("context", "prompt")

@patch('requests.post')
def test_successful_compression(mock_post, compressor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {
            "compressed_prompt": "compressed output",
            "original_prompt_tokens": 100,
            "compressed_prompt_tokens": 50
        },
        "latency_ms": 120,
        "model_used": "scaledown-v1"
    }
    mock_post.return_value = mock_response

    result = compressor.compress(context="long context", prompt="short prompt")
    
    assert isinstance(result, sd.CompressedPrompt)
    assert result.content == "compressed output"
    assert result.tokens == (100, 50)
    assert result.savings_percent == 50.0

@patch('requests.post')
def test_batch_compression(mock_post, compressor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {
            "compressed_prompt": "compressed",
            "original_prompt_tokens": 10,
            "compressed_prompt_tokens": 5
        }
    }
    mock_post.return_value = mock_response

    contexts = ["ctx1", "ctx2"]
    prompts = ["p1", "p2"]
    
    results = compressor.compress(context=contexts, prompt=prompts)
    
    assert len(results) == 2
    assert isinstance(results[0], sd.CompressedPrompt)

@pytest.mark.skipif(
    not os.environ.get("SCALEDOWN_API_KEY"),
    reason="Skipping live API test because SCALEDOWN_API_KEY is not set"
)
def test_live_api_call():
    """Integration test against the real API."""
    api_key = os.environ["SCALEDOWN_API_KEY"]
    comp = sd.ScaleDownCompressor(api_key=api_key)
    
    try:
        result = comp.compress(
            context="This is a test context that is longer than the prompt.",
            prompt="Summarize this"
        )
        assert isinstance(result, sd.CompressedPrompt)
        assert len(result.content) > 0
    except Exception as e:
        pytest.fail(f"Live API call failed: {e}")
