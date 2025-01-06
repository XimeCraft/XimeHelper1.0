"""
Base knowledge base service interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class KnowledgeBaseService(ABC):
    """Base class for knowledge base services"""
    
    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize knowledge base service
        
        Args:
            **kwargs: Additional service-specific parameters
        """
        self.kwargs = kwargs
    
    @abstractmethod
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the knowledge base
        
        Args:
            content: Document content
            metadata: Additional metadata for the document
            
        Returns:
            Document ID
        """
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching documents with their metadata
        """
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str):
        """Delete a document from the knowledge base
        
        Args:
            doc_id: ID of the document to delete
        """
        pass 