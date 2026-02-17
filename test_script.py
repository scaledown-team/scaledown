import os
import tempfile
import time
import scaledown as sd 

# Optional Optimizers (Lazy Loaded)
from scaledown.optimizer import HasteOptimizer, SemanticOptimizer
from scaledown.exceptions import AuthenticationError, APIError


API_KEY = os.environ.get("SCALEDOWN_API_KEY", "yVlJ8qWWVF6wj8RZUfNHm7fUYqNBVEFr3Rrfep67")
sd.set_api_key(API_KEY)

if API_KEY == "your_api_key_here":
    print("Warning: Using placeholder API key. API calls will fail.")
    print("Export your key: export SCALEDOWN_API_KEY='sk_...'\n")

TEST_CODE = """
def calculate_sum(numbers):
    \"\"\"Calculate sum of numbers.\"\"\"
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_average(numbers):
    \"\"\"Calculate average of numbers.\"\"\"
    if len(numbers) == 0:
        return 0
    return calculate_sum(numbers) / len(numbers)

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return calculate_average(self.data)
"""

def print_header(title):
    print("\n" + "-" * 60)
    print(f"{title}")
    print("-" * 60)

def print_step_details(step_name, content, metrics):
    print(f"\n[{step_name}]")
    
    # Handle different metric structures safely
    in_tok = metrics.get('original_tokens', metrics.get('input_tokens', '?'))
    out_tok = metrics.get('optimized_tokens', metrics.get('compressed_tokens', metrics.get('output_tokens', '?')))
    
    print(f"Tokens: {in_tok} -> {out_tok}")
    
    if 'latency_ms' in metrics:
        print(f"Latency: {metrics['latency_ms']:.0f}ms")
    
    preview = content.strip()[:150].replace('\n', ' ')
    print(f"Preview: {preview}{'...' if len(content) > 150 else ''}")

# main test logic
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(TEST_CODE)
    file_path_arg = f.name

try:
    print_header("Component tests")

    # 1. test semantic
    print("\nTesting SemanticOptimizer...", end=" ")
    try:
        opt = SemanticOptimizer(top_k=1)
        res = opt.optimize(context=TEST_CODE, query="DataProcessor", file_path=file_path_arg)
        print("Passed")
        
        metrics_dict = res.metrics.__dict__ if hasattr(res.metrics, '__dict__') else {}
        print_step_details("Semantic output", res.content, metrics_dict)
    except ImportError:
        print("Skipped (missing dependencies)")
    except Exception as e:
        print(f"Failed: {e}")

    # 2. test haste
    print("\nTesting HasteOptimizer...", end=" ")
    try:
        opt = HasteOptimizer(top_k=2)
        res = opt.optimize(context=TEST_CODE, query="calculate_average", file_path=file_path_arg, target_model="gpt-4o")
        print("Passed")
        
        metrics_dict = res.metrics.__dict__ if hasattr(res.metrics, '__dict__') else {}
        print_step_details("Haste output", res.content, metrics_dict)
    except ImportError:
         print("Skipped (missing dependencies)")
    except Exception as e:
        print(f"Failed: {e}")

    # 3. test compressor
    print("\nTesting ScaleDownCompressor...", end=" ")
    try:
        comp = sd.ScaleDownCompressor(target_model="gpt-4o")
        res = comp.compress(context=TEST_CODE, prompt="Summarize")
        print("Passed")
        
        metrics_dict = {
            "original_tokens": res.tokens[0], 
            "compressed_tokens": res.tokens[1],
            "latency_ms": 0 
        }
        print_step_details("Compressor output", res.content, metrics_dict)
    except Exception as e:
        print(f"Failed: {e}")

    # 4. full pipeline
    print_header("Pipeline integration")
    
    steps = []
    try:
        steps.append(('haste', HasteOptimizer(top_k=5)))
    except ImportError: pass
    
    try:
        steps.append(('semantic', SemanticOptimizer(top_k=1)))
    except ImportError: pass
        
    steps.append(('compressor', sd.ScaleDownCompressor(target_model="gpt-4o")))

    pipeline = sd.Pipeline(steps)
    print(f"Configuration: {[s[0] for s in steps]}")

    result = pipeline.run(
        context=TEST_CODE,
        query="logic for processing",
        file_path=file_path_arg,
        prompt="Explain logic"
    )
    
    print("Pipeline finished successfully")
    
    print("\n--- Trace ---")
    for i, step in enumerate(result.history):
        print(f"\nStep {i+1}: {step.step_name}")
        print(f"  Latency: {step.latency_ms:.0f}ms")
        print(f"  Tokens:  {step.input_tokens} -> {step.output_tokens}")
        

    print_header("Summary")
    print(f"Original size: {len(TEST_CODE)} chars")
    print(f"Final size:    {len(result.final_content)} chars")
    print(f"Savings:       {result.savings_percent:.1f}%")

except Exception as e:
    print(f"\nError: {e}")

finally:
    if os.path.exists(file_path_arg):
        os.unlink(file_path_arg)
