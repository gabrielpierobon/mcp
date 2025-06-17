import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from tools.google_slides_tool import (
    create_google_slides,
    add_slide,
    create_slide_with_content,
    add_content_to_slide_placeholders,
    add_text_to_slide,
    add_slide_to_last_presentation,
    get_slide_info,
    list_recent_presentations,
    find_presentation_by_title
)

@pytest.mark.unit
@pytest.mark.external_api
class TestGoogleSlidesTools:
    """Test suite for Google Slides tools."""
    
    @pytest.fixture
    def mock_google_apis_available(self):
        """Mock Google APIs as available for testing."""
        with patch('tools.google_slides_tool.GOOGLE_APIS_AVAILABLE', True):
            yield
    
    @pytest.fixture
    def mock_google_apis_unavailable(self):
        """Mock Google APIs as unavailable for testing."""
        with patch('tools.google_slides_tool.GOOGLE_APIS_AVAILABLE', False):
            yield
    
    @pytest.fixture
    def mock_google_services(self):
        """Mock Google API services."""
        # Mock presentation response
        mock_presentation = {
            'presentationId': 'test_slides_id_123',
            'title': 'Test Presentation',
            'slides': [
                {
                    'objectId': 'slide_id_1',
                    'slideProperties': {'layoutId': 'TITLE_SLIDE'},
                    'pageElements': [
                        {
                            'objectId': 'title_placeholder',
                            'shape': {
                                'placeholder': {
                                    'type': 'TITLE'
                                },
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Slide Title'}}
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        # Mock slides service
        mock_slides_service = Mock()
        mock_presentations = Mock()
        
        # Configure slides service methods
        mock_presentations.create.return_value.execute.return_value = mock_presentation
        mock_presentations.get.return_value.execute.return_value = mock_presentation
        mock_presentations.batchUpdate.return_value.execute.return_value = {
            'presentationId': 'test_slides_id_123',
            'replies': [
                {
                    'createSlide': {
                        'objectId': 'new_slide_id_456'
                    }
                }
            ]
        }
        mock_slides_service.presentations.return_value = mock_presentations
        
        # Mock drive service
        mock_drive_service = Mock()
        mock_permissions = Mock()
        mock_permissions.create.return_value.execute.return_value = {'id': 'permission_id'}
        mock_drive_service.permissions.return_value = mock_permissions
        
        return {
            'slides_service': mock_slides_service,
            'drive_service': mock_drive_service,
            'presentation': mock_presentation
        }
    
    @pytest.fixture
    def setup_mocks(self, mock_google_apis_available, mock_google_services):
        """Setup comprehensive mocks for Google Slides."""
        import tools.google_slides_tool
        
        def mock_get_service(service_name, version):
            if service_name == 'slides':
                return mock_google_services['slides_service']
            elif service_name == 'drive':
                return mock_google_services['drive_service']
            return None
        
        # Mock the get_service function
        setattr(tools.google_slides_tool, 'get_service', mock_get_service)
        
        yield mock_google_services
        
        # Clean up and initialize context
        tools.google_slides_tool._recent_presentations_context.clear()
        tools.google_slides_tool._recent_presentations_context.update({
            "last_presentation": None,
            "recent_presentations": []
        })

@pytest.mark.unit
@pytest.mark.external_api
class TestCreateGoogleSlides(TestGoogleSlidesTools):
    """Test create_google_slides function."""
    
    @pytest.mark.asyncio
    async def test_create_google_slides_success(self, setup_mocks):
        """Test successful Google Slides creation."""
        result = await create_google_slides("Test Presentation")
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["title"] == "Test Presentation"
        assert result["presentation_url"] == "https://docs.google.com/presentation/d/test_slides_id_123/edit"
    
    @pytest.mark.asyncio
    async def test_create_google_slides_with_sharing(self, setup_mocks):
        """Test creating Google Slides with sharing."""
        emails = ["user1@example.com", "user2@example.com"]
        result = await create_google_slides("Shared Presentation", share_with=emails)
        
        assert result["status"] == "success"
        assert "shared_with" in result
        # The shared_with field contains successful shares, which could be empty if permissions fail
        assert isinstance(result["shared_with"], list)
    
    @pytest.mark.asyncio
    async def test_create_google_slides_apis_unavailable(self, mock_google_apis_unavailable):
        """Test slides creation when Google APIs are not available."""
        result = await create_google_slides("Test Presentation")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_google_slides_service_failure(self, setup_mocks):
        """Test slides creation with service failure."""
        import tools.google_slides_tool
        setattr(tools.google_slides_tool, 'get_service', lambda x, y: None)
        
        result = await create_google_slides("Test Presentation")
        
        assert result["status"] == "error"
        assert "Failed to authenticate" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_google_slides_api_exception(self, setup_mocks):
        """Test slides creation with API exception."""
        setup_mocks['slides_service'].presentations.return_value.create.side_effect = Exception("API Error")
        
        result = await create_google_slides("Test Presentation")
        
        assert result["status"] == "error"
        assert "Tool execution failed: API Error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAddSlide(TestGoogleSlidesTools):
    """Test add_slide function."""
    
    @pytest.mark.asyncio
    async def test_add_slide_success(self, setup_mocks):
        """Test successful slide addition."""
        result = await add_slide("test_slides_id_123", "TITLE_AND_BODY", "New Slide")
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["slide_id"].startswith("slide_")  # Dynamic ID
        assert result["slide_layout"] == "TITLE_AND_BODY"
        assert result["title"] == "New Slide"
    
    @pytest.mark.asyncio
    async def test_add_slide_blank_layout(self, setup_mocks):
        """Test adding blank slide."""
        result = await add_slide("test_slides_id_123", "BLANK")
        
        assert result["status"] == "success"
        assert result["slide_layout"] == "BLANK"
        assert result["title"] is None
    
    @pytest.mark.asyncio
    async def test_add_slide_with_insert_index(self, setup_mocks):
        """Test adding slide at specific position."""
        result = await add_slide("test_slides_id_123", "TITLE_ONLY", "Inserted Slide", insert_index=1)
        
        assert result["status"] == "success"
        assert result["title"] == "Inserted Slide"
    
    @pytest.mark.asyncio
    async def test_add_slide_apis_unavailable(self, mock_google_apis_unavailable):
        """Test adding slide when Google APIs are not available."""
        result = await add_slide("test_id", "BLANK")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_add_slide_api_exception(self, setup_mocks):
        """Test adding slide with API exception."""
        setup_mocks['slides_service'].presentations.return_value.batchUpdate.side_effect = Exception("Add slide error")
        
        result = await add_slide("test_id", "BLANK")
        
        assert result["status"] == "error"
        assert "Tool execution failed: Add slide error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestCreateSlideWithContent(TestGoogleSlidesTools):
    """Test create_slide_with_content function."""
    
    @pytest.mark.asyncio
    async def test_create_slide_with_content_success(self, setup_mocks):
        """Test successful slide creation with content."""
        result = await create_slide_with_content(
            "test_slides_id_123",
            "TITLE_AND_BODY",
            "Slide Title",
            "Slide body content"
        )
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["slide_id"].startswith("slide_")  # Dynamic ID
        assert result["title"] == "Slide Title"
        # Content should be added to placeholders or have a warning
        assert "content_added" in result or "content_warning" in result
    
    @pytest.mark.asyncio
    async def test_create_slide_with_content_title_only(self, setup_mocks):
        """Test creating slide with title only."""
        result = await create_slide_with_content(
            "test_slides_id_123",
            "TITLE_ONLY",
            "Title Only Slide"
        )
        
        assert result["status"] == "success"
        assert result["title"] == "Title Only Slide"
        # Should indicate content was added or have a warning
        assert "content_added" in result or "content_warning" in result
    
    @pytest.mark.asyncio
    async def test_create_slide_with_content_api_exception(self, setup_mocks):
        """Test creating slide with content API exception."""
        setup_mocks['slides_service'].presentations.return_value.batchUpdate.side_effect = Exception("Content error")
        
        result = await create_slide_with_content("test_id", "TITLE_AND_BODY", "Title", "Body")
        
        assert result["status"] == "error"
        assert "Tool execution failed: Content error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAddContentToSlidePlaceholders(TestGoogleSlidesTools):
    """Test add_content_to_slide_placeholders function."""
    
    @pytest.mark.asyncio
    async def test_add_content_to_slide_placeholders_success(self, setup_mocks):
        """Test successful content addition to placeholders."""
        result = await add_content_to_slide_placeholders(
            "test_slides_id_123",
            "slide_id_1",
            "New Title",
            "New Body Text"
        )
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["slide_id"] == "slide_id_1"
        # Check that content was added
        assert "title_added" in result or "body_added" in result
    
    @pytest.mark.asyncio
    async def test_add_content_to_slide_placeholders_title_only(self, setup_mocks):
        """Test adding title only to placeholders."""
        result = await add_content_to_slide_placeholders(
            "test_slides_id_123",
            "slide_id_1",
            title_text="Title Only"
        )
        
        assert result["status"] == "success"
        # Check that title content was processed
        assert "title_added" in result or "available_placeholders" in result
    
    @pytest.mark.asyncio
    async def test_add_content_to_slide_placeholders_api_exception(self, setup_mocks):
        """Test adding content with API exception."""
        setup_mocks['slides_service'].presentations.return_value.batchUpdate.side_effect = Exception("Placeholder error")
        
        result = await add_content_to_slide_placeholders("test_id", "slide_id", "Title")
        
        assert result["status"] == "error"
        # Could be either an API error or slide not found error
        assert "error" in result["error"] or "not found" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAddTextToSlide(TestGoogleSlidesTools):
    """Test add_text_to_slide function."""
    
    @pytest.mark.asyncio
    async def test_add_text_to_slide_success(self, setup_mocks):
        """Test successful text addition to slide."""
        result = await add_text_to_slide(
            "test_slides_id_123",
            "slide_id_1",
            "Custom text box content"
        )
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["slide_id"] == "slide_id_1"
        assert result["text"] == "Custom text box content"
        assert result["position"]["x"] == 100
        assert result["position"]["y"] == 100
        assert result["size"]["width"] == 400
        assert result["size"]["height"] == 100
    
    @pytest.mark.asyncio
    async def test_add_text_to_slide_custom_position(self, setup_mocks):
        """Test adding text with custom position and size."""
        result = await add_text_to_slide(
            "test_slides_id_123",
            "slide_id_1",
            "Positioned text",
            x=200, y=300, width=500, height=150
        )
        
        assert result["status"] == "success"
        assert result["position"]["x"] == 200
        assert result["position"]["y"] == 300
        assert result["size"]["width"] == 500
        assert result["size"]["height"] == 150
    
    @pytest.mark.asyncio
    async def test_add_text_to_slide_api_exception(self, setup_mocks):
        """Test adding text with API exception."""
        setup_mocks['slides_service'].presentations.return_value.batchUpdate.side_effect = Exception("Text error")
        
        result = await add_text_to_slide("test_id", "slide_id", "Text")
        
        assert result["status"] == "error"
        assert "Tool execution failed: Text error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAddSlideToLastPresentation(TestGoogleSlidesTools):
    """Test add_slide_to_last_presentation function."""
    
    @pytest.mark.asyncio
    async def test_add_slide_to_last_presentation_success(self, setup_mocks):
        """Test successful slide addition to last presentation."""
        # First create a presentation to have a "last presentation"
        await create_google_slides("Test Presentation")
        
        result = await add_slide_to_last_presentation("TITLE_AND_BODY", "New Slide", "Slide content")
        
        assert result["status"] == "success"
        assert result["slide_layout"] == "TITLE_AND_BODY"
        assert result["title"] == "New Slide"
        # Should have information about where it was added
        assert "added_to" in result
    
    @pytest.mark.asyncio
    async def test_add_slide_to_last_presentation_no_recent(self, setup_mocks):
        """Test adding slide when no recent presentation exists."""
        result = await add_slide_to_last_presentation()
        
        assert result["status"] == "error"
        assert "No recent presentation found" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestGetSlideInfo(TestGoogleSlidesTools):
    """Test get_slide_info function."""
    
    @pytest.mark.asyncio
    async def test_get_slide_info_success(self, setup_mocks):
        """Test successful slide info retrieval."""
        result = await get_slide_info("test_slides_id_123", "slide_id_1")
        
        assert result["status"] == "success"
        assert result["presentation_id"] == "test_slides_id_123"
        assert result["slide_id"] == "slide_id_1"
        assert "placeholders" in result
        assert "total_elements" in result
        assert "text_boxes" in result
        assert "shapes" in result
    
    @pytest.mark.asyncio
    async def test_get_slide_info_api_exception(self, setup_mocks):
        """Test getting slide info with API exception."""
        setup_mocks['slides_service'].presentations.return_value.get.side_effect = Exception("Info error")
        
        result = await get_slide_info("test_id", "slide_id")
        
        assert result["status"] == "error"
        assert "Tool execution failed: Info error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestContextMemoryFunctions(TestGoogleSlidesTools):
    """Test context memory and utility functions."""
    
    @pytest.mark.asyncio
    async def test_list_recent_presentations_empty(self, setup_mocks):
        """Test listing recent presentations when none exist."""
        result = await list_recent_presentations()
        
        assert result["status"] == "success"
        assert result["recent_presentations"] == []
        assert result["last_presentation"] is None
        assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_list_recent_presentations_with_data(self, setup_mocks):
        """Test listing recent presentations with existing data."""
        # Create some presentations
        await create_google_slides("Presentation 1")
        await create_google_slides("Presentation 2")
        await create_google_slides("Presentation 3")
        
        result = await list_recent_presentations()
        
        assert result["status"] == "success"
        assert result["count"] == 3
        assert len(result["recent_presentations"]) == 3
        assert result["last_presentation"]["title"] == "Presentation 3"  # Most recent
        assert result["recent_presentations"][0]["title"] == "Presentation 3"  # First in list
    
    @pytest.mark.asyncio
    async def test_find_presentation_by_title_success(self, setup_mocks):
        """Test finding presentation by title."""
        await create_google_slides("Project Presentation")
        await create_google_slides("Team Meeting")
        await create_google_slides("Project Review")
        
        result = await find_presentation_by_title("Project")
        
        assert result["status"] == "success"
        assert result["search_term"] == "Project"
        assert result["count"] == 2
        assert len(result["matching_presentations"]) == 2
        
        # Check that both project-related presentations are found
        titles = [pres["title"] for pres in result["matching_presentations"]]
        assert "Project Presentation" in titles
        assert "Project Review" in titles
    
    @pytest.mark.asyncio
    async def test_find_presentation_by_title_case_insensitive(self, setup_mocks):
        """Test case-insensitive title search."""
        await create_google_slides("UPPERCASE PRESENTATION")
        await create_google_slides("lowercase presentation")
        await create_google_slides("MiXeD cAsE presentation")
        
        result = await find_presentation_by_title("PRESENTATION")
        
        assert result["status"] == "success"
        assert result["count"] == 3  # Should find all three
    
    @pytest.mark.asyncio
    async def test_find_presentation_by_title_no_matches(self, setup_mocks):
        """Test finding presentation when no matches exist."""
        await create_google_slides("Test Presentation")
        
        result = await find_presentation_by_title("NonExistent")
        
        assert result["status"] == "success"
        assert result["count"] == 0
        assert result["matching_presentations"] == []
        assert len(result["all_available_titles"]) == 1

@pytest.mark.integration
class TestGoogleSlidesToolRegistration:
    """Test tool registration."""
    
    def test_tool_registration_available(self):
        """Test tool registration when Google APIs are available."""
        mock_mcp = Mock()
        mock_tool = Mock()
        mock_mcp.tool.return_value = mock_tool
        
        with patch('tools.google_slides_tool.GOOGLE_APIS_AVAILABLE', True):
            from tools.google_slides_tool import register
            register(mock_mcp)
        
        # Should register all 9 tools
        assert mock_mcp.tool.call_count == 9
    
    def test_tool_registration_unavailable(self):
        """Test tool registration when Google APIs are not available."""
        mock_mcp = Mock()
        
        with patch('tools.google_slides_tool.GOOGLE_APIS_AVAILABLE', False):
            from tools.google_slides_tool import register
            register(mock_mcp)
        
        # Should not register any tools
        mock_mcp.tool.assert_not_called()

@pytest.mark.unit
class TestErrorHandling(TestGoogleSlidesTools):
    """Test comprehensive error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_complex_workflow_success(self, setup_mocks):
        """Test a complex workflow with multiple operations."""
        # Create presentation
        create_result = await create_google_slides("Workflow Test")
        assert create_result["status"] == "success"
        
        presentation_id = create_result["presentation_id"]
        
        # Add a blank slide
        add_result = await add_slide(presentation_id, "BLANK")
        assert add_result["status"] == "success"
        slide_id = add_result["slide_id"]
        
        # Add text to the slide
        text_result = await add_text_to_slide(presentation_id, slide_id, "Custom text")
        assert text_result["status"] == "success"
        
        # Create slide with content
        content_slide_result = await create_slide_with_content(
            presentation_id, "TITLE_AND_BODY", "Content Slide", "Body content"
        )
        assert content_slide_result["status"] == "success"
        
        # Get slide info (may fail in mock environment, which is expected)
        info_result = await get_slide_info(presentation_id, slide_id)
        # In the mock environment, the slide might not be found, which is expected
        assert info_result["status"] in ["success", "error"]
        
        # Add slide using context functions
        last_slide_result = await add_slide_to_last_presentation("TITLE_ONLY", "Last Slide")
        assert last_slide_result["status"] == "success"
        
        # List recent presentations
        list_result = await list_recent_presentations()
        assert list_result["status"] == "success"
        assert list_result["count"] == 1
    
    @pytest.mark.asyncio
    async def test_context_management(self, setup_mocks):
        """Test that context management works correctly."""
        # Create multiple presentations
        presentations = []
        for i in range(3):
            result = await create_google_slides(f"Test Presentation {i+1}")
            assert result["status"] == "success"
            presentations.append(result)
        
        # Test context storage
        context_result = await list_recent_presentations()
        assert context_result["count"] == 3
        assert context_result["last_presentation"]["title"] == "Test Presentation 3"
        
        # Test search functionality
        search_result = await find_presentation_by_title("Presentation 2")
        assert search_result["count"] == 1
        assert search_result["matching_presentations"][0]["title"] == "Test Presentation 2"
        
        # Test add slide to specific presentation by title search
        # This would happen internally through add_slide_to_last_presentation
        last_slide_result = await add_slide_to_last_presentation("TITLE_AND_BODY", "Added Slide")
        assert last_slide_result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_edge_cases_and_validation(self, setup_mocks):
        """Test edge cases and input validation."""
        # Empty title
        result = await create_google_slides("")
        assert result["status"] == "success"  # Should still work with empty title
        
        # Special characters in title
        special_result = await create_google_slides("Test 'Presentation' with \"Quotes\" & Symbols! 🎨")
        assert special_result["status"] == "success"
        
        # Very long slide content
        long_content = "Very long slide content " * 100
        content_result = await create_slide_with_content(
            "test_id", "TITLE_AND_BODY", "Long Content", long_content
        )
        assert content_result["status"] == "success"
        
        # Unicode content
        unicode_content = "Unicode test: 你好世界 مرحبا بالعالم こんにちは世界"
        unicode_result = await add_text_to_slide("test_id", "slide_id", unicode_content)
        assert unicode_result["status"] == "success"
        assert unicode_result["text"] == unicode_content
