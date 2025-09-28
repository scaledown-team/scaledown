# ScaleDown - AI Prompt Optimization Package

ScaleDown is a Python package for creating, managing, and optimizing AI prompt templates.
It helps reduce token usage while preserving semantic meaning, saving costs and improving
response quality from AI models like Claude and GPT.

## Installation

```bash
pip install scaledown
```

## Sample Usage

```python
from scaledown.tools import tools
result = tools(llm='gemini-1.5-flash', optimiser='cot')
llm_provider = result['llm_provider']
optimizer = result['optimizer']
```
