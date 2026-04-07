"""
Setup utilities for LangChain notebooks and applications.

Provides easy initialization of Azure OpenAI LLMs and embeddings,
along with standard environment setup.
"""

from .llm import create_azure_llm, create_azure_embedding

__version__ = "1.0.0"
__all__ = [
    "create_azure_llm",
    "create_azure_embedding",
    "setup",
]


def setup():
    """
    Initialize the environment for LangChain applications.
    
    This function:
    - Loads environment variables from .env file
    - Adds necessary module paths
    - Prints initialization status
    
    Returns:
        None
        
    Example:
        >>> from setup_utils import setup
        >>> setup()
        Environment initialization completed successfully.
    """
    from dotenv import load_dotenv
    from pathlib import Path
    import sys
    
    # Load environment variables
    load_dotenv()
    
    # Add module7-genai-langchain to path if needed
    module_path = Path(__file__).parent.parent
    if str(module_path) not in sys.path:
        sys.path.append(str(module_path))
    
    print("Environment initialization completed successfully.")
