"""
Setup Utilities Module

A reusable Python module for initializing Azure OpenAI LLMs and embeddings 
in notebooks and scripts.

## Installation

Add to your notebooks:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("../module7-genai-langchain").resolve()))
```

## Quick Start

```python
from setup_utils import setup, create_azure_llm, create_azure_embedding

# Initialize environment
setup()

# Create LLM
llm = create_azure_llm()

# Create embeddings
embeddings = create_azure_embedding()

# Use them
response = llm.invoke("Hello!")
print(response.content)
```

## Environment Variables

Set these in your `.env` file:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

## API Reference

### setup()
Initialize environment and load variables.

```python
from setup_utils import setup
setup()
```

### create_azure_llm(deployment_type="chat", temperature=0.7)
Create a configured Azure OpenAI language model.

**Parameters:**
- `deployment_type` (str): "chat" or "audio" (default: "chat")
- `temperature` (float): Sampling temperature 0-1 (default: 0.7)

**Returns:** AzureChatOpenAI instance

**Example:**
```python
from setup_utils import create_azure_llm

# Default settings
llm = create_azure_llm()

# Custom temperature (more deterministic)
llm = create_azure_llm(temperature=0.3)

# Use it
response = llm.invoke("What is 2+2?")
print(response.content)
```

### create_azure_embedding()
Create a configured Azure OpenAI embedding model.

**Returns:** AzureOpenAIEmbeddings instance

**Example:**
```python
from setup_utils import create_azure_embedding

embeddings = create_azure_embedding()
vector = embeddings.embed_query("Hello world")
print(len(vector))  # Dimension of embedding
```

## Common Patterns

### In Notebooks

**Cell 1: Setup**
```python
import sys
from pathlib import Path

# Add module path
sys.path.insert(0, str(Path("../module7-genai-langchain").resolve()))

# Setup environment
from setup_utils import setup
setup()
```

**Cell 2: Use LLM**
```python
from setup_utils import create_azure_llm

llm = create_azure_llm()
response = llm.invoke("Hello, how are you?")
print(response.content)
```

### In Scripts

```python
#!/usr/bin/env python
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path("module7-genai-langchain").resolve()))

# Import and setup
from setup_utils import setup, create_azure_llm

setup()
llm = create_azure_llm()

# Use the LLM
response = llm.invoke("Your prompt here")
print(response.content)
```

### With Events Planner Module

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("../module7-genai-langchain").resolve()))

from setup_utils import setup, create_azure_llm
from event_planner import create_coordinator_with_memory, send_message_with_checkpointer
from langchain.messages import HumanMessage

setup()
coordinator = create_coordinator_with_memory(llm=create_azure_llm())

# Use the event planner...
```

## Troubleshooting

### "Missing Azure OpenAI endpoint or API key"
- Ensure you've created a `.env` file in the project root
- Check that `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` are set
- Verify the keys are valid in Azure Portal

### "Missing AZURE_OPENAI_CHAT_DEPLOYMENT"
- Ensure `AZURE_OPENAI_CHAT_DEPLOYMENT` is set in `.env`
- Verify this deployment exists in your Azure OpenAI resource
- Check the deployment name matches exactly (case-sensitive)

### "ModuleNotFoundError: No module named 'setup_utils'"
- Make sure you've added the module to Python path:
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path("path/to/module7-genai-langchain").resolve()))
  ```

## Features

✨ **Easy to Use**: Simple functions, sensible defaults
🔧 **Configurable**: Customize temperature, deployment type, etc.
📝 **Well Documented**: Comprehensive docstrings and examples
🚀 **Production Ready**: Error handling and validation built-in
🔐 **Secure**: Uses environment variables for sensitive data

## Version

v1.0.0
