"""
Tests for Vector Database
"""

import pytest
from backend.database.vector_db import VectorDatabase

def test_vector_db_initialization():
    """Test vector database initialization"""
    db = VectorDatabase()
    assert db is not None
    assert db.embedding_model is not None

def test_get_collection_stats():
    """Test collection statistics"""
    db = VectorDatabase()
    stats = db.get_collection_stats()
    assert "document_count" in stats
    assert isinstance(stats["document_count"], int)

def test_fallback_knowledge():
    """Test fallback knowledge generation"""
    db = VectorDatabase()
    knowledge = db._get_fallback_knowledge()
    assert len(knowledge) > 0
    assert all(isinstance(k, str) for k in knowledge)

def test_text_chunking():
    """Test text chunking"""
    db = VectorDatabase()
    text = "This is a test sentence. " * 100
    chunks = db._chunk_text(text)
    assert len(chunks) > 0
    assert all(len(chunk) <= 1200 for chunk in chunks)  # chunk_size + some buffer

def test_search_functionality():
    """Test search functionality"""
    db = VectorDatabase()
    
    # Initialize with fallback if empty
    if db.get_collection_stats()["document_count"] == 0:
        db.initialize_from_pdf()
    
    results = db.search("chronic kidney disease", n_results=3)
    assert isinstance(results, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
