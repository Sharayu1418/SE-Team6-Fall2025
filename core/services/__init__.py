"""
Service layer for AutoGen agents.

This module provides:
- DjangoMCPService: MCP-style interface to Django models
- OllamaClient: Centralized client for Ollama LLM interactions
"""

from .django_mcp import DjangoMCPService
from .ollama_client import OllamaClient

__all__ = [
    "DjangoMCPService",
    "OllamaClient",
]




