# ScaleDown v0.1.3 - Advanced AI Prompt Optimization Package
ScaleDown is a comprehensive Python package for creating, managing, and optimizing AI prompt templates with advanced modular optimization techniques. It integrates template management, style systems, and cutting-edge prompt optimization methods to reduce hallucinations and improve AI response quality.

## Key Features

### **Modular Prompt Optimization**
- **5 Advanced Optimizers**: Expert Persona, Chain-of-Thought, Uncertainty Quantification, Chain-of-Verification, and baseline
- **8 Pre-built Optimization Styles**: Expert Thinking, Verified Expert, Careful Reasoning, and more
- **Composable Pipeline**: Combine multiple optimizers in any sequence
- **Hallucination Reduction**: Specialized techniques to minimize AI hallucinations

### **Professional Template System**
- **Template Management**: Create and manage reusable prompt templates
- **Variable Substitution**: Dynamic placeholder replacement
- **Category Organization**: Organize templates by domain and use case
- **Template Optimization**: Apply optimizers to templates automatically

### **Multi-LLM Integration**
- **Universal LLM Support**: OpenAI GPT, Google Gemini, ScaleDown models
- **Unified Interface**: Consistent API across all model providers
- **Token Management**: Smart token counting and limit handling
- **Model Optimization**: Model-specific prompt optimization

### **Backward Compatibility**
- **Legacy API Support**: Existing code continues to work unchanged
- **Enhanced Features**: Opt-in advanced functionality
- **Migration Path**: Seamless upgrade from basic to advanced usage

## Installation

```bash
pip install scaledown
```

# Quick Start

### Basic Usage (Backward Compatible)
```python
from scaledown.tools import tools
result = tools(llm='gemini-1.5-flash', optimiser='cot')
llm_provider = result['llm_provider']
optimizer = result['optimizer']
```

### Enhanced Usage with Optimization Pipeline
```python
from scaledown import ScaleDown

# Initialize with optimization features
sd = ScaleDown()

# Select model and optimization style
sd.select_model('scaledown-gpt-4o')

# Optimize and call LLM in one step
result = sd.optimize_and_call_llm(
    question="Explain quantum computing principles",
    optimizers=['expert_persona', 'cot', 'uncertainty'],
    max_tokens=500
)

print(f"Optimized Response: {result['llm_response']}")
print(f"Optimization Report: {result['optimization_metrics']}")
```

### Direct Optimization (Simple API)
```python
from scaledown import optimize_prompt, parse_optimizers

# Parse optimizers
optimizers = parse_optimizers('expert_persona,cot,uncertainty')

# Optimize prompt
question = "What are the implications of artificial general intelligence?"
optimized_prompt = optimize_prompt(question, optimizers)

print(f"Original: {question}")
print(f"Optimized: {optimized_prompt}")
```

## Available Optimizers

| Optimizer | Description | Use Case |
|-----------|-------------|----------|
| `expert_persona` | Adds domain expertise context | Specialized knowledge tasks |
| `cot` | Chain-of-Thought reasoning | Complex problem solving |
| `uncertainty` | Confidence assessment | Critical decision making |
| `cove` | Chain-of-Verification | Fact-checking and accuracy |
| `none` | Baseline (no optimization) | Performance comparison |

## Pre-built Optimization Styles

| Style | Optimizers | Best For |
|-------|------------|----------|
| Expert Thinking | `expert_persona + cot` | Research and analysis |
| Verified Expert | `expert_persona + cove` | Fact-based responses |
| Careful Reasoning | `cot + uncertainty` | Cautious decision making |
| Comprehensive Analysis | `all optimizers` | Critical tasks |

