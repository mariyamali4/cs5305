from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader

from mcp.shared.exceptions import McpError
from mcp.types import CallToolResult, TextContent

from dotenv import load_dotenv
import sys
import asyncio
import subprocess
import io
from pathlib import Path
from pprint import pprint

sys.path.append(str(Path("../module7-genai-langchain").resolve()))
from azure_openai_llm import create_azure_llm

load_dotenv()
print("Environment initializing completed successfully.")
