import pytest
import asyncio
from unittest.mock import patch, AsyncMock, Mock, MagicMock
from typing import Dict, Any
import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the tool functions
from tools.rag_knowledge_base_tool import (
    setup_knowledge_base,
    get_kb_health,
    add_url_to_kb,
    add_text_to_kb,
    search_kb,
    list_kb_sources,
    get_kb_stats,
    CHROMADB_AVAILABLE,
    SENTENCE_TRANSFORMERS_AVAILABLE,
    LANGCHAIN_AVAILABLE
)

# Test class for RAG infrastructure operations
@pytest.mark.unit
@pytest.mark.external_api
class TestRAGInfrastructure:
    """Test RAG knowledge base infrastructure setup and health monitoring."""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup comprehensive mocks for RAG dependencies."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Mock ChromaDB
            mock_collection = Mock()
            mock_collection.add = Mock()
            mock_collection.query = Mock(return_value={
                'documents': [['test doc']],
                'metadatas': [[{'test': True}]],
                'distances': [[0.1]]
            })
            
            mock_client = Mock()
            mock_client.get_or_create_collection = Mock(return_value=mock_collection)
            mock_client.create_collection = Mock(return_value=mock_collection)
            mock_client.get_collection = Mock(return_value=mock_collection)
            mock_client.delete_collection = Mock()
            
            # Mock SentenceTransformer
            mock_model = Mock()
            mock_model.encode = Mock(return_value=Mock(tolist=Mock(return_value=[[0.1, 0.2, 0.3]])))
            
            # Mock TextSplitter
            mock_splitter = Mock()
            mock_splitter.split_text = Mock(return_value=['chunk1', 'chunk2'])
            
            with patch('tools.rag_knowledge_base_tool._initialize_chroma', return_value=mock_client), \
                 patch('tools.rag_knowledge_base_tool._initialize_embedding_model', return_value=mock_model), \
                 patch('tools.rag_knowledge_base_tool._initialize_text_splitter', return_value=mock_splitter), \
                 patch('tools.rag_knowledge_base_tool.KNOWLEDGE_BASE_DIR') as mock_dir, \
                 patch('tools.rag_knowledge_base_tool._get_config_path') as mock_config_path:
                
                # Setup temporary directories
                temp_dir = Path(tempfile.mkdtemp())
                mock_dir.mkdir = Mock()
                mock_config_path.return_value = temp_dir / "kb_config.json"
                
                yield {
                    'client': mock_client,
                    'model': mock_model,
                    'splitter': mock_splitter,
                    'collection': mock_collection,
                    'temp_dir': temp_dir
                }
                
                # Cleanup
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_setup_knowledge_base_success(self, setup_mocks):
        """Test successful knowledge base setup."""
        result = await setup_knowledge_base()
        
        assert result["status"] == "success"
        assert "RAG Knowledge Base infrastructure setup complete" in result["message"]
        assert "config" in result
        assert "components" in result
        assert "test_results" in result
        
        # Check components
        assert result["components"]["chroma_client"] == "initialized"
        assert result["components"]["embedding_model"] == "loaded"
        assert result["components"]["text_splitter"] == "configured"
        assert result["components"]["default_collection"] == "ready"
        
        # Check test results
        assert result["test_results"]["embedding_test"] == "passed"
        assert result["test_results"]["storage_test"] == "passed"
        assert "chunks" in result["test_results"]["chunking_test"]
    
    @pytest.mark.asyncio
    async def test_setup_knowledge_base_missing_dependencies(self):
        """Test setup with missing dependencies."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=False,
            SENTENCE_TRANSFORMERS_AVAILABLE=False,
            LANGCHAIN_AVAILABLE=False
        ):
            result = await setup_knowledge_base()
            
            assert result["status"] == "error"
            assert "Missing dependencies" in result["error"]
            assert "chromadb" in result["error"]
            assert "sentence-transformers" in result["error"]
            assert "langchain-text-splitters" in result["error"]
            assert "install_command" in result
    
    @pytest.mark.asyncio
    async def test_setup_knowledge_base_partial_dependencies(self):
        """Test setup with only some dependencies missing."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=False,
            LANGCHAIN_AVAILABLE=True
        ):
            result = await setup_knowledge_base()
            
            assert result["status"] == "error"
            assert "sentence-transformers" in result["error"]
            assert "chromadb" not in result["error"]
            assert "langchain-text-splitters" not in result["error"]
    
    @pytest.mark.asyncio
    async def test_setup_knowledge_base_initialization_error(self, setup_mocks):
        """Test setup with component initialization error."""
        with patch('tools.rag_knowledge_base_tool._initialize_chroma', side_effect=Exception("ChromaDB init failed")):
            result = await setup_knowledge_base()
            
            assert result["status"] == "error"
            assert "Setup failed" in result["error"]
            assert "ChromaDB init failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_kb_health_success(self, setup_mocks):
        """Test successful health check."""
        mocks = setup_mocks
        mocks['client'].list_collections.return_value = ['default', 'test']
        
        result = await get_kb_health()
        
        assert result["status"] == "healthy"
        assert result["components"]["database"]["status"] == "connected"
        assert result["components"]["embedding_model"]["status"] == "loaded"
        assert result["components"]["text_splitter"] == "configured"
        assert result["components"]["database"]["collections"] == 2
    
    @pytest.mark.asyncio
    async def test_get_kb_health_missing_dependencies(self):
        """Test health check with missing dependencies."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=False,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            result = await get_kb_health()
            
            assert result["status"] == "unhealthy"
            assert "Missing required dependencies" in result["error"]
            assert result["components"]["dependencies"]["chromadb"] == False
    
    @pytest.mark.asyncio
    async def test_get_kb_health_component_error(self, setup_mocks):
        """Test health check with component errors."""
        with patch('tools.rag_knowledge_base_tool._initialize_chroma', side_effect=Exception("DB connection failed")):
            result = await get_kb_health()
            
            assert result["status"] == "unhealthy"
            assert "DB connection failed" in result["error"]


# Test class for content ingestion operations
@pytest.mark.unit
@pytest.mark.external_api  
class TestRAGContentIngestion:
    """Test RAG content ingestion from URLs and text."""
    
    @pytest.fixture
    def setup_ingestion_mocks(self):
        """Setup mocks for content ingestion tests."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Mock collection
            mock_collection = Mock()
            mock_collection.add = Mock()
            
            # Mock client
            mock_client = Mock()
            mock_client.get_or_create_collection = Mock(return_value=mock_collection)
            
            # Mock embedding model
            mock_model = Mock()
            mock_embeddings = Mock()
            mock_embeddings.tolist.return_value = [[0.1, 0.2], [0.3, 0.4]]
            mock_model.encode = Mock(return_value=mock_embeddings)
            
            # Mock text splitter
            mock_splitter = Mock()
            mock_splitter.split_text = Mock(return_value=['chunk 1 content', 'chunk 2 content'])
            
            with patch('tools.rag_knowledge_base_tool._initialize_chroma', return_value=mock_client), \
                 patch('tools.rag_knowledge_base_tool._initialize_embedding_model', return_value=mock_model), \
                 patch('tools.rag_knowledge_base_tool._initialize_text_splitter', return_value=mock_splitter):
                
                yield {
                    'client': mock_client,
                    'model': mock_model,
                    'splitter': mock_splitter,
                    'collection': mock_collection
                }
    
    @pytest.mark.asyncio
    async def test_add_url_to_kb_success(self, setup_ingestion_mocks):
        """Test successful URL content ingestion."""
        # Mock successful crawl result
        mock_crawl_result = {
            "status": "success",
            "markdown": "# Test Article\n\nThis is test content from a webpage. It contains multiple paragraphs of information that should be chunked appropriately for the knowledge base."
        }
        
        with patch('tools.crawl4ai_tool.crawl_webpage', return_value=mock_crawl_result):
            result = await add_url_to_kb("https://example.com/article", "test_collection", {"topic": "testing"})
            
            assert result["status"] == "success"
            assert "Successfully added URL content" in result["message"]
            assert result["url"] == "https://example.com/article"
            assert result["collection"] == "test_collection"
            assert result["chunks_added"] == 2
            assert result["total_characters"] > 0
            assert len(result["chunk_ids"]) <= 5  # Shows first 5 IDs (or all if fewer)
            
            # Verify components were called
            mocks = setup_ingestion_mocks
            mocks['splitter'].split_text.assert_called_once()
            mocks['model'].encode.assert_called_once()
            mocks['collection'].add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_url_to_kb_crawl_failure(self, setup_ingestion_mocks):
        """Test URL ingestion with crawl failure."""
        mock_crawl_result = {
            "error": "Failed to load webpage",
            "status": "error"
        }
        
        with patch('tools.crawl4ai_tool.crawl_webpage', return_value=mock_crawl_result):
            result = await add_url_to_kb("https://invalid-url.com")
            
            assert result["status"] == "error"
            assert "Failed to scrape URL" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_url_to_kb_empty_content(self, setup_ingestion_mocks):
        """Test URL ingestion with empty content."""
        mock_crawl_result = {
            "status": "success",
            "markdown": ""  # Empty content
        }
        
        with patch('tools.crawl4ai_tool.crawl_webpage', return_value=mock_crawl_result):
            result = await add_url_to_kb("https://example.com/empty")
            
            assert result["status"] == "error"
            assert "No meaningful content extracted" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_url_to_kb_crawl_tool_unavailable(self, setup_ingestion_mocks):
        """Test URL ingestion when crawl tool is unavailable."""
        # Mock the import to fail inside the function
        with patch.dict('sys.modules', {'tools.crawl4ai_tool': None}):
            result = await add_url_to_kb("https://example.com")
            
            assert result["status"] == "error"
            assert "crawl_webpage tool not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_url_to_kb_processing_error(self, setup_ingestion_mocks):
        """Test URL ingestion with processing error."""
        mock_crawl_result = {
            "status": "success",
            "markdown": "x"  # Content too short (< 50 chars)
        }
        
        with patch('tools.crawl4ai_tool.crawl_webpage', return_value=mock_crawl_result):
            result = await add_url_to_kb("https://example.com")
            
            assert result["status"] == "error"
            assert "No meaningful content extracted" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_text_to_kb_success(self, setup_ingestion_mocks):
        """Test successful text content ingestion."""
        test_text = "This is a comprehensive test document that contains multiple sentences. It should be properly chunked and stored in the knowledge base with appropriate metadata."
        
        result = await add_text_to_kb(test_text, "test_document", "custom_collection", {"author": "test_user"})
        
        assert result["status"] == "success"
        assert "Successfully added text content" in result["message"]
        assert result["source_name"] == "test_document"
        assert result["collection"] == "custom_collection"
        assert result["chunks_added"] == 2
        assert result["total_characters"] == len(test_text)
        
        # Verify processing
        mocks = setup_ingestion_mocks
        mocks['splitter'].split_text.assert_called_with(test_text)
        mocks['model'].encode.assert_called_once()
        mocks['collection'].add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_text_to_kb_short_text(self, setup_ingestion_mocks):
        """Test text ingestion with text too short."""
        result = await add_text_to_kb("short", "test_doc")
        
        assert result["status"] == "error"
        assert "Text content is too short" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_text_to_kb_no_chunks(self, setup_ingestion_mocks):
        """Test text ingestion when no chunks are generated."""
        mocks = setup_ingestion_mocks
        mocks['splitter'].split_text.return_value = []  # No chunks
        
        result = await add_text_to_kb("Valid content for testing", "test_doc")
        
        assert result["status"] == "error"
        assert "No chunks generated from text" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_text_to_kb_embedding_error(self, setup_ingestion_mocks):
        """Test text ingestion with embedding error."""
        mocks = setup_ingestion_mocks
        mocks['model'].encode.side_effect = Exception("Model loading failed")
        
        result = await add_text_to_kb("Valid content for testing", "test_doc")
        
        assert result["status"] == "error"
        assert "Failed to add text" in result["error"]


# Test class for search and retrieval operations
@pytest.mark.unit
@pytest.mark.external_api
class TestRAGSearchRetrieval:
    """Test RAG search and retrieval functionality."""
    
    @pytest.fixture
    def setup_search_mocks(self):
        """Setup mocks for search and retrieval tests."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Mock search results
            mock_search_results = {
                'documents': [['This is the first result', 'This is the second result']],
                'metadatas': [[
                    {
                        'source_url': 'https://example.com/doc1',
                        'source_type': 'webpage',
                        'timestamp': '2024-01-01T00:00:00',
                        'chunk_index': 0,
                        'chunk_length': 25,
                        'token_count': 5
                    },
                    {
                        'source_name': 'test_document',
                        'source_type': 'text',
                        'timestamp': '2024-01-02T00:00:00',
                        'chunk_index': 1,
                        'chunk_length': 26,
                        'token_count': 5
                    }
                ]],
                'distances': [[0.2, 0.3]]
            }
            
            # Mock collection
            mock_collection = Mock()
            mock_collection.query = Mock(return_value=mock_search_results)
            mock_collection.get = Mock(return_value={
                'metadatas': [
                    {'source_url': 'https://example.com/doc1', 'source_type': 'webpage', 'chunk_length': 100},
                    {'source_name': 'test_doc', 'source_type': 'text', 'chunk_length': 150}
                ]
            })
            
            # Mock client
            mock_client = Mock()
            mock_client.get_collection = Mock(return_value=mock_collection)
            mock_client.list_collections = Mock(return_value=[Mock(name='default'), Mock(name='test')])
            
            # Mock embedding model
            mock_model = Mock()
            mock_embeddings = Mock()
            mock_embeddings.tolist.return_value = [[0.1, 0.2, 0.3]]
            mock_model.encode = Mock(return_value=mock_embeddings)
            
            # Mock config
            mock_config = {
                "embedding": {"model_name": "test-model"},
                "chunking": {"chunk_size": 1000, "chunk_overlap": 100},
                "storage": {"database_path": "./test_db"}
            }
            
            with patch('tools.rag_knowledge_base_tool._initialize_chroma', return_value=mock_client), \
                 patch('tools.rag_knowledge_base_tool._initialize_embedding_model', return_value=mock_model), \
                 patch('tools.rag_knowledge_base_tool._load_config', return_value=mock_config), \
                 patch('tools.rag_knowledge_base_tool._get_config_path') as mock_config_path:
                
                # Setup temporary directory for config
                temp_dir = Path(tempfile.mkdtemp())
                mock_config_path.return_value = temp_dir / "kb_config.json"
                
                yield {
                    'client': mock_client,
                    'model': mock_model,
                    'collection': mock_collection,
                    'search_results': mock_search_results,
                    'temp_dir': temp_dir
                }
                
                # Cleanup
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_search_kb_success(self, setup_search_mocks):
        """Test successful knowledge base search."""
        result = await search_kb("machine learning", "default", 5, True)
        
        assert result["status"] == "success"
        assert result["query"] == "machine learning"
        assert result["collection"] == "default"
        assert result["total_results"] == 2
        assert len(result["results"]) == 2
        
        # Check first result
        first_result = result["results"][0]
        assert first_result["rank"] == 1
        assert first_result["content"] == "This is the first result"
        assert first_result["similarity_score"] == 0.8  # 1 - 0.2
        assert first_result["metadata"]["source"] == "https://example.com/doc1"
        assert first_result["metadata"]["source_type"] == "webpage"
        
        # Check search stats
        assert "search_stats" in result
        assert result["search_stats"]["embedding_model"] == "test-model"
    
    @pytest.mark.asyncio
    async def test_search_kb_no_results(self, setup_search_mocks):
        """Test search with no results."""
        mocks = setup_search_mocks
        mocks['collection'].query.return_value = {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        
        result = await search_kb("nonexistent query")
        
        assert result["status"] == "success"
        assert result["total_results"] == 0
        assert result["results"] == []
        assert "No results found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_search_kb_short_query(self, setup_search_mocks):
        """Test search with query too short."""
        result = await search_kb("ab")  # Only 2 characters
        
        assert result["status"] == "error"
        assert "Query is too short" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_kb_invalid_limit(self, setup_search_mocks):
        """Test search with invalid limit."""
        result = await search_kb("test query", limit=100)  # Exceeds max of 50
        
        assert result["status"] == "error"
        assert "Limit must be between 1 and 50" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_kb_collection_not_found(self, setup_search_mocks):
        """Test search with non-existent collection."""
        mocks = setup_search_mocks
        mocks['client'].get_collection.side_effect = Exception("Collection not found")
        
        result = await search_kb("test query", "nonexistent")
        
        assert result["status"] == "error"
        assert "Collection 'nonexistent' not found" in result["error"]
        assert "available_collections" in result
    
    @pytest.mark.asyncio
    async def test_search_kb_without_metadata(self, setup_search_mocks):
        """Test search without including metadata."""
        result = await search_kb("test query", include_metadata=False)
        
        assert result["status"] == "success"
        for res in result["results"]:
            assert "metadata" not in res or not res["metadata"]
    
    @pytest.mark.asyncio
    async def test_search_kb_processing_error(self, setup_search_mocks):
        """Test search with processing error."""
        mocks = setup_search_mocks
        mocks['model'].encode.side_effect = Exception("Embedding failed")
        
        result = await search_kb("test query")
        
        assert result["status"] == "error"
        assert "Search failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_kb_sources_success(self, setup_search_mocks):
        """Test successful listing of knowledge base sources."""
        result = await list_kb_sources("default")
        
        assert result["status"] == "success"
        assert result["collection"] == "default"
        assert result["total_sources"] == 2
        assert result["total_chunks"] == 2
        assert len(result["sources"]) == 2
        
        # Check source structure
        first_source = result["sources"][0]
        assert "source" in first_source
        assert "source_type" in first_source
        assert "chunk_count" in first_source
        
        # Check summary
        assert "summary" in result
        assert "source_types" in result["summary"]
    
    @pytest.mark.asyncio
    async def test_list_kb_sources_empty_collection(self, setup_search_mocks):
        """Test listing sources from empty collection."""
        mocks = setup_search_mocks
        mocks['collection'].get.return_value = {'metadatas': []}
        
        result = await list_kb_sources("default")
        
        assert result["status"] == "success"
        assert result["total_sources"] == 0
        assert result["total_chunks"] == 0
        assert result["sources"] == []
        assert "No sources found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_list_kb_sources_collection_not_found(self, setup_search_mocks):
        """Test listing sources from non-existent collection."""
        mocks = setup_search_mocks
        mocks['client'].get_collection.side_effect = Exception("Collection not found")
        
        result = await list_kb_sources("nonexistent")
        
        assert result["status"] == "error"
        assert "Collection 'nonexistent' not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_kb_stats_success(self, setup_search_mocks):
        """Test successful retrieval of knowledge base statistics."""
        mocks = setup_search_mocks
        
        # Mock collection data for stats
        mock_collection_data = {
            'metadatas': [
                {'source_url': 'https://example.com', 'source_type': 'webpage'},
                {'source_name': 'doc1', 'source_type': 'text'}
            ]
        }
        mocks['collection'].get.return_value = mock_collection_data
        
        result = await get_kb_stats()
        
        assert result["status"] == "success"
        assert "overview" in result
        assert "collections" in result
        assert "configuration" in result
        
        # Check configuration
        assert result["configuration"]["embedding_model"] == "test-model"
        assert result["configuration"]["chunk_size"] == 1000
        
        # Check overview
        assert result["overview"]["total_collections"] >= 0
        assert result["overview"]["total_chunks"] >= 0
        assert result["overview"]["total_sources"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_kb_stats_no_collections(self, setup_search_mocks):
        """Test stats retrieval with no collections."""
        mocks = setup_search_mocks
        mocks['client'].list_collections.return_value = []
        
        result = await get_kb_stats()
        
        assert result["status"] == "success"
        assert result["overview"]["total_collections"] == 0
        assert result["overview"]["total_chunks"] == 0
        assert result["overview"]["total_sources"] == 0
    
    @pytest.mark.asyncio
    async def test_get_kb_stats_processing_error(self, setup_search_mocks):
        """Test stats retrieval with processing error."""
        # Override the mock to cause an error during initialization 
        with patch('tools.rag_knowledge_base_tool._initialize_chroma', side_effect=Exception("Database error")):
            result = await get_kb_stats()
            
            assert result["status"] == "error"
            assert "Failed to get stats" in result["error"]


# Test class for RAG tool registration and error handling
@pytest.mark.unit
class TestRAGToolRegistration:
    """Test RAG tool registration and error handling."""
    
    def test_tool_registration_available(self, fastmcp_server):
        """Test tool registration when dependencies are available."""
        from tools.rag_knowledge_base_tool import register
        
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Mock server instance
            mock_server = Mock()
            mock_server.tool = Mock(return_value=lambda func: func)
            
            # Should not raise any exceptions
            register(mock_server)
            
            # Verify tools were registered (7 calls for 7 functions)
            assert mock_server.tool.call_count == 7
    
    def test_tool_registration_unavailable(self, fastmcp_server):
        """Test tool registration when dependencies are unavailable."""
        from tools.rag_knowledge_base_tool import register
        
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=False,
            SENTENCE_TRANSFORMERS_AVAILABLE=False,
            LANGCHAIN_AVAILABLE=False
        ):
            # Mock server instance
            mock_server = Mock()
            mock_server.tool = Mock(return_value=lambda func: func)
            
            # Should return early without registering tools
            register(mock_server)
            
            # Verify no tools were registered
            assert mock_server.tool.call_count == 0


# Test class for comprehensive error handling and edge cases
@pytest.mark.unit
@pytest.mark.external_api
class TestRAGErrorHandling:
    """Test comprehensive error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_complex_workflow_success(self):
        """Test a complex workflow with multiple operations."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Mock components for full workflow
            mock_collection = Mock()
            mock_collection.add = Mock()
            mock_collection.query = Mock(return_value={
                'documents': [['test result']],
                'metadatas': [[{'source_name': 'workflow_test'}]],
                'distances': [[0.1]]
            })
            
            mock_client = Mock()
            mock_client.get_or_create_collection = Mock(return_value=mock_collection)
            mock_client.get_collection = Mock(return_value=mock_collection)
            mock_client.list_collections = Mock(return_value=[Mock(name='test')])
            
            mock_model = Mock()
            mock_model.encode = Mock(return_value=Mock(tolist=Mock(return_value=[[0.1, 0.2]])))
            
            mock_splitter = Mock()
            mock_splitter.split_text = Mock(return_value=['test chunk'])
            
            with patch('tools.rag_knowledge_base_tool._initialize_chroma', return_value=mock_client), \
                 patch('tools.rag_knowledge_base_tool._initialize_embedding_model', return_value=mock_model), \
                 patch('tools.rag_knowledge_base_tool._initialize_text_splitter', return_value=mock_splitter), \
                 patch('tools.rag_knowledge_base_tool._get_config_path') as mock_config_path:
                
                temp_dir = Path(tempfile.mkdtemp())
                mock_config_path.return_value = temp_dir / "kb_config.json"
                
                try:
                    # 1. Setup knowledge base
                    setup_result = await setup_knowledge_base()
                    assert setup_result["status"] == "success"
                    
                    # 2. Add content
                    add_result = await add_text_to_kb("Test content for workflow", "workflow_test")
                    assert add_result["status"] == "success"
                    
                    # 3. Search content
                    search_result = await search_kb("workflow test")
                    assert search_result["status"] == "success"
                    
                    # 4. Get stats
                    stats_result = await get_kb_stats()
                    assert stats_result["status"] == "success"
                    
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_context_management(self):
        """Test context management and resource cleanup."""
        with patch.multiple(
            'tools.rag_knowledge_base_tool',
            CHROMADB_AVAILABLE=True,
            SENTENCE_TRANSFORMERS_AVAILABLE=True,
            LANGCHAIN_AVAILABLE=True
        ):
            # Test that multiple operations don't interfere with each other
            mock_client = Mock()
            mock_model = Mock()
            mock_splitter = Mock()
            
            with patch('tools.rag_knowledge_base_tool._initialize_chroma', return_value=mock_client), \
                 patch('tools.rag_knowledge_base_tool._initialize_embedding_model', return_value=mock_model), \
                 patch('tools.rag_knowledge_base_tool._initialize_text_splitter', return_value=mock_splitter):
                
                # Multiple health checks shouldn't cause issues
                health1 = await get_kb_health()
                health2 = await get_kb_health()
                
                assert health1["status"] == "healthy"
                assert health2["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_edge_cases_and_validation(self):
        """Test edge cases and input validation."""
        # Test with various edge case inputs
        
        # Empty query
        result = await search_kb("")
        assert result["status"] == "error"
        
        # Whitespace-only query
        result = await search_kb("   ")
        assert result["status"] == "error"
        
        # Zero limit
        result = await search_kb("test", limit=0)
        assert result["status"] == "error"
        
        # Negative limit
        result = await search_kb("test", limit=-1)
        assert result["status"] == "error"
        
        # Excessive limit
        result = await search_kb("test", limit=1000)
        assert result["status"] == "error"


# Integration test for basic tool registration
@pytest.mark.integration
class TestToolRegistration:
    """Test basic tool registration functionality."""
    
    def test_basic_registration(self, fastmcp_server):
        """Test that tools can be registered without errors."""
        from tools.rag_knowledge_base_tool import register
        
        # This should not raise any exceptions regardless of dependency availability
        try:
            register(fastmcp_server)
        except Exception as e:
            pytest.fail(f"Tool registration should not raise exceptions: {e}") 