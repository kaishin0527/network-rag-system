
"""
Network RAG System

A RAG-based network configuration generation system that uses
retrieval-augmented generation to create network configurations
based on predefined knowledge bases.
"""

__version__ = "1.0.0"
__author__ = "Network RAG System Team"
__email__ = "team@network-rag.com"

from .rag_system import NetworkRAGSystem
from .config_generator import NetworkConfigGenerator
from .knowledge_base import KnowledgeBase, DevicePolicy

__all__ = [
    "NetworkRAGSystem",
    "NetworkConfigGenerator", 
    "KnowledgeBase",
    "DevicePolicy",
]
