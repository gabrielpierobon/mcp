import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from tools.google_docs_tool import (
    create_google_doc,
    rewrite_last_doc,
    rewrite_document,
    read_google_doc,
    list_recent_documents
)

@pytest.mark.unit
@pytest.mark.external_api
class TestGoogleDocsTools:
    """Test suite for Google Docs tools."""
    
    @pytest.fixture
    def mock_google_apis_available(self):
        """Mock Google APIs as available for testing."""
        with patch('tools.google_docs_tool.GOOGLE_APIS_AVAILABLE', True):
            yield
    
    @pytest.fixture
    def mock_google_apis_unavailable(self):
        """Mock Google APIs as unavailable for testing."""
        with patch('tools.google_docs_tool.GOOGLE_APIS_AVAILABLE', False):
            yield
    
    @pytest.fixture
    def mock_google_services(self):
        """Mock Google API services."""
        # Mock document response
        mock_document = {
            'documentId': 'test_doc_id_123',
            'title': 'Test Document',
            'body': {
                'content': [
                    {
                        'paragraph': {
                            'elements': [
                                {
                                    'textRun': {
                                        'content': 'Test document content\n'
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        # Mock docs service
        mock_docs_service = Mock()
        mock_documents = Mock()
        
        # Configure docs service methods
        mock_documents.create.return_value.execute.return_value = mock_document
        mock_documents.get.return_value.execute.return_value = mock_document
        mock_documents.batchUpdate.return_value.execute.return_value = {
            'replies': [{'createNamedRange': {'namedRangeId': 'test_range'}}]
        }
        mock_docs_service.documents.return_value = mock_documents
        
        # Mock drive service
        mock_drive_service = Mock()
        mock_permissions = Mock()
        mock_permissions.create.return_value.execute.return_value = {'id': 'permission_id'}
        mock_drive_service.permissions.return_value = mock_permissions
        
        return {
            'docs_service': mock_docs_service,
            'drive_service': mock_drive_service,
            'document': mock_document
        }
    
    @pytest.fixture
    def setup_mocks(self, mock_google_apis_available, mock_google_services):
        """Setup comprehensive mocks for Google Docs."""
        import tools.google_docs_tool
        
        def mock_get_service(service_name, version):
            if service_name == 'docs':
                return mock_google_services['docs_service']
            elif service_name == 'drive':
                return mock_google_services['drive_service']
            return None
        
        # Mock the get_service function
        setattr(tools.google_docs_tool, 'get_service', mock_get_service)
        
        yield mock_google_services
        
        # Clean up and initialize context
        tools.google_docs_tool._recent_documents_context.clear()
        tools.google_docs_tool._recent_documents_context.update({
            "last_document": None,
            "recent_documents": []
        })

@pytest.mark.unit
@pytest.mark.external_api
class TestCreateGoogleDoc(TestGoogleDocsTools):
    """Test create_google_doc function."""
    
    @pytest.mark.asyncio
    async def test_create_google_doc_success(self, setup_mocks):
        """Test successful Google Doc creation."""
        result = await create_google_doc("Test Document", "This is test content.")
        
        assert result["status"] == "success"
        assert result["document_id"] == "test_doc_id_123"
        assert result["title"] == "Test Document"
        assert result["document_url"] == "https://docs.google.com/document/d/test_doc_id_123/edit"
        assert result["content_length"] == len("This is test content.")
    
    @pytest.mark.asyncio
    async def test_create_google_doc_with_sharing(self, setup_mocks):
        """Test creating Google Doc with sharing."""
        emails = ["user1@example.com", "user2@example.com"]
        result = await create_google_doc("Shared Doc", "Shared content", share_with=emails)
        
        assert result["status"] == "success"
        assert "shared_with" in result
        # The shared_with field contains successful shares, which could be empty if permissions fail
        assert isinstance(result["shared_with"], list)
    
    @pytest.mark.asyncio
    async def test_create_google_doc_apis_unavailable(self, mock_google_apis_unavailable):
        """Test doc creation when Google APIs are not available."""
        result = await create_google_doc("Test Doc", "Content")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestRewriteLastDoc(TestGoogleDocsTools):
    """Test rewrite_last_doc function."""
    
    @pytest.mark.asyncio
    async def test_rewrite_last_doc_success(self, setup_mocks):
        """Test successful rewriting of last document."""
        # First create a document to have a "last document"
        await create_google_doc("Test Doc", "Original content")
        
        new_content = "This is the new content for the document."
        result = await rewrite_last_doc(new_content)
        
        assert result["status"] == "success"
        assert result["document_id"] == "test_doc_id_123"
        assert result["new_content_length"] == len(new_content)
    
    @pytest.mark.asyncio
    async def test_rewrite_last_doc_no_recent_doc(self, setup_mocks):
        """Test rewriting when no recent document exists."""
        new_content = "New content"
        result = await rewrite_last_doc(new_content)
        
        assert result["status"] == "error"
        assert "No recent document found" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestRewriteDocument(TestGoogleDocsTools):
    """Test rewrite_document function."""
    
    @pytest.mark.asyncio
    async def test_rewrite_document_success(self, setup_mocks):
        """Test successful document rewriting by ID."""
        new_content = "Completely new document content."
        result = await rewrite_document("test_doc_id_123", new_content)
        
        assert result["status"] == "success"
        assert result["document_id"] == "test_doc_id_123"
        assert result["new_content_length"] == len(new_content)

@pytest.mark.unit
@pytest.mark.external_api
class TestReadGoogleDoc(TestGoogleDocsTools):
    """Test read_google_doc function."""
    
    @pytest.mark.asyncio
    async def test_read_google_doc_success(self, setup_mocks):
        """Test successful document reading."""
        result = await read_google_doc("test_doc_id_123")
        
        assert result["status"] == "success"
        assert result["document_id"] == "test_doc_id_123"
        assert result["title"] == "Test Document"
        assert "content" in result
        assert "Test document content" in result["content"]

@pytest.mark.unit
@pytest.mark.external_api
class TestListRecentDocuments(TestGoogleDocsTools):
    """Test list_recent_documents function."""
    
    @pytest.mark.asyncio
    async def test_list_recent_documents_empty(self, setup_mocks):
        """Test listing recent documents when none exist."""
        result = await list_recent_documents()
        
        assert result["status"] == "success"
        assert result["recent_documents"] == []
        assert result["last_document"] is None
        assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_list_recent_documents_with_data(self, setup_mocks):
        """Test listing recent documents with existing data."""
        # Create some documents
        await create_google_doc("Doc 1", "Content 1")
        await create_google_doc("Doc 2", "Content 2")
        await create_google_doc("Doc 3", "Content 3")
        
        result = await list_recent_documents()
        
        assert result["status"] == "success"
        assert result["count"] == 3
        assert len(result["recent_documents"]) == 3
        assert result["last_document"]["title"] == "Doc 3"  # Most recent
        assert result["recent_documents"][0]["title"] == "Doc 3"  # First in list

@pytest.mark.integration
class TestGoogleDocsToolRegistration:
    """Test tool registration."""
    
    def test_tool_registration_available(self):
        """Test tool registration when Google APIs are available."""
        mock_mcp = Mock()
        mock_tool = Mock()
        mock_mcp.tool.return_value = mock_tool
        
        with patch('tools.google_docs_tool.GOOGLE_APIS_AVAILABLE', True):
            from tools.google_docs_tool import register
            register(mock_mcp)
        
        # Should register all 5 tools
        assert mock_mcp.tool.call_count == 5
    
    def test_tool_registration_unavailable(self):
        """Test tool registration when Google APIs are not available."""
        mock_mcp = Mock()
        
        with patch('tools.google_docs_tool.GOOGLE_APIS_AVAILABLE', False):
            from tools.google_docs_tool import register
            register(mock_mcp)
        
        # Should not register any tools
        mock_mcp.tool.assert_not_called()
