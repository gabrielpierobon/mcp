import pytest
import asyncio
import os
import tempfile
import shutil
import warnings
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import sys
from pathlib import Path

# Comprehensive Pydantic deprecation warning suppression at import time
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")
warnings.filterwarnings("ignore", message=".*class-based.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")
warnings.filterwarnings("ignore", message="Support for class-based `config` is deprecated.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pydantic.*config.*deprecated.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*ConfigDict.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Pydantic.*deprecated.*", category=DeprecationWarning)
# Catch any pydantic related deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*pydantic.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*fastmcp.*")
# Suppress specific module warnings that may be causing issues
warnings.filterwarnings("ignore", category=DeprecationWarning, module="starlette.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.*")

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock fastmcp module at the module level to prevent import errors
if 'fastmcp' not in sys.modules:
    class MockFastMCP:
        def __init__(self, name):
            self.name = name
            self._tool_manager = Mock()
            self._tool_manager._tools = {}
            
        def tool(self):
            def decorator(func):
                self._tool_manager._tools[func.__name__] = func
                return func
            return decorator
            
        def run(self):
            pass
    
    mock_fastmcp = Mock()
    mock_fastmcp.FastMCP = MockFastMCP
    sys.modules['fastmcp'] = mock_fastmcp

# Removed deprecated event_loop fixture - using pytest-asyncio's default

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'BRAVE_API_KEY': 'test_brave_key',
        'AIRTABLE_PERSONAL_ACCESS_TOKEN': 'test_airtable_token',
        'GOOGLE_CREDENTIALS_FILE': 'test_credentials.json',
        'GOOGLE_TOKEN_FILE': 'test_token.json',
        'MCP_SERVER_NAME': 'test-mcp-server',
        'MCP_HOST': 'localhost',
        'MCP_PORT': '8000'
    }):
        yield

@pytest.fixture
def temp_playground_dir():
    """Create a temporary playground directory for file writing tests."""
    temp_dir = tempfile.mkdtemp(prefix="test_playground_")
    temp_path = Path(temp_dir)
    
    # Patch the PLAYGROUND_ROOT constant in the file writing tool
    with patch('tools.file_writing_tool.PLAYGROUND_ROOT', temp_path):
        yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def temp_file_system():
    """Create a temporary file system for file system tests."""
    temp_dir = tempfile.mkdtemp(prefix="test_fs_")
    
    # Create some test files and directories
    test_files = {
        'test.txt': 'Hello, world!',
        'data.json': '{"key": "value"}',
        'subdir/nested.py': 'print("nested file")',
        'empty_file.txt': '',
        'large_file.txt': 'x' * 1000
    }
    
    for file_path, content in test_files.items():
        full_path = Path(temp_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for external API calls."""
    mock_client = AsyncMock()
    
    # Create a mock for the AsyncClient constructor result that has async context manager behavior
    mock_async_client_instance = AsyncMock()
    mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_client)
    mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
    
    with patch('httpx.AsyncClient', return_value=mock_async_client_instance):
        yield mock_async_client_instance

@pytest.fixture
def mock_brave_search_response():
    """Mock response for Brave Search API."""
    return {
        "web": {
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "description": "Test description 1"
                },
                {
                    "title": "Test Result 2", 
                    "url": "https://example.com/2",
                    "description": "Test description 2"
                }
            ],
            "totalCount": 2
        },
        "news": {"results": []},
        "videos": {"results": []},
        "mixed": {}
    }

@pytest.fixture
def mock_weather_response():
    """Mock response for weather API (Open-Meteo format)."""
    return {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "utc_offset_seconds": -18000,
        "timezone": "America/New_York",
        "current_weather": {
            "temperature": 20.5,
            "windspeed": 8.2,
            "weathercode": 0
        },
        "hourly": {
            "time": ["2024-01-01T00:00", "2024-01-01T01:00", "2024-01-01T02:00", "2024-01-01T03:00"],
            "temperature_2m": [20.5, 21.0, 20.8, 20.2],
            "weathercode": [0, 1, 2, 0]
        },
        "hourly_units": {
            "temperature_2m": "°C"
        },
        "current_weather_units": {
            "windspeed": "km/h"
        }
    }

@pytest.fixture
def mock_airtable_response():
    """Mock response for Airtable API."""
    return {
        "records": [
            {
                "id": "rec123",
                "fields": {
                    "Name": "Test Record",
                    "Value": 42
                },
                "createdTime": "2024-01-01T00:00:00.000Z"
            }
        ]
    }

@pytest.fixture
def mock_google_credentials():
    """Mock Google API credentials."""
    mock_creds = Mock()
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh = Mock()
    
    with patch('google.auth.default', return_value=(mock_creds, 'test-project')):
        with patch('googleapiclient.discovery.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service
            yield mock_service

@pytest.fixture
def mock_screen_capture():
    """Mock screen capture functionality."""
    from PIL import Image
    import io
    
    # Create a simple test image
    test_image = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Mock the availability flags and the mss module at the tools level
    with patch('tools.screen_capture_tool.MSS_AVAILABLE', True):
        with patch('tools.screen_capture_tool.PILLOW_AVAILABLE', True):
            with patch('tools.screen_capture_tool.mss', create=True) as mock_mss_module:
                # Configure mock screenshot data with proper attributes
                mock_screenshot_data = Mock()
                mock_screenshot_data.bgra = b'fake_bgra_data' * 25  # 100x100 would need 40000 bytes, approximate
                mock_screenshot_data.size = (100, 100)
                
                # Mock monitor configuration
                mock_monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                
                mock_sct = Mock()
                mock_sct.shot.return_value = 'test_screenshot.png'
                mock_sct.grab.return_value = mock_screenshot_data
                mock_sct.monitors = [mock_monitor, mock_monitor]  # Index 0 (all) and 1 (primary)
                mock_mss_module.mss.return_value.__enter__.return_value = mock_sct
                
                with patch('tools.screen_capture_tool.pyautogui', create=True) as mock_pyautogui:
                    mock_pyautogui.screenshot.return_value = test_image
                    with patch('PIL.Image.frombytes', return_value=test_image):
                        with patch('tools.screen_capture_tool._copy_image_to_clipboard', return_value=True):
                            yield mock_sct

@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser functionality."""
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    
    mock_context.new_page.return_value = mock_page
    mock_browser.new_context.return_value = mock_context
    
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_p = AsyncMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_p
        yield mock_browser, mock_page, mock_context

@pytest.fixture
def mock_crawl4ai():
    """Mock Crawl4AI functionality."""
    mock_crawler = AsyncMock()
    mock_result = Mock()
    mock_result.markdown = "# Test Content\nThis is test content."
    mock_result.cleaned_html = "<h1>Test Content</h1><p>This is test content.</p>"
    mock_result.success = True
    mock_result.status_code = 200
    
    mock_crawler.arun.return_value = mock_result
    
    with patch('crawl4ai.AsyncWebCrawler', return_value=mock_crawler):
        yield mock_crawler

@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB for RAG knowledge base testing."""
    mock_collection = Mock()
    mock_collection.add = Mock()
    mock_collection.query.return_value = {
        'documents': [['Test document content']],
        'metadatas': [[{'source': 'test.txt'}]],
        'distances': [[0.1]]
    }
    mock_collection.count.return_value = 5
    
    mock_client = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    with patch('chromadb.Client', return_value=mock_client):
        with patch('chromadb.PersistentClient', return_value=mock_client):
            yield mock_client, mock_collection

@pytest.fixture
def mock_sentence_transformers():
    """Mock sentence transformers for embeddings."""
    mock_model = Mock()
    mock_model.encode.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
    
    with patch('sentence_transformers.SentenceTransformer', return_value=mock_model):
        yield mock_model

@pytest.fixture
def sample_calculation_data():
    """Sample data for calculator tests."""
    return [
        {"operation": "add", "num1": 5, "num2": 3, "expected": 8},
        {"operation": "subtract", "num1": 10, "num2": 4, "expected": 6},
        {"operation": "multiply", "num1": 6, "num2": 7, "expected": 42},
        {"operation": "divide", "num1": 15, "num2": 3, "expected": 5},
    ]

@pytest.fixture
def fastmcp_server():
    """Create a FastMCP server instance for testing."""
    # Mock the FastMCP server to avoid import dependency
    mock_server = Mock()
    mock_tool_manager = Mock()
    mock_tool_manager._tools = {}
    mock_server._tool_manager = mock_tool_manager
    
    # Track registered functions
    registered_functions = []
    
    # Mock the decorator method to properly track tool registration
    def mock_tool_decorator():
        def decorator(func):
            # Store the function in the tool manager
            mock_tool_manager._tools[func.__name__] = func
            registered_functions.append(func.__name__)
            return func
        return decorator
    
    # Create a Mock that can be called and also has call_count
    mock_tool_method = Mock(side_effect=mock_tool_decorator)
    mock_server.tool = mock_tool_method
    
    # Add the registered functions list as an attribute for tests to access
    mock_server._registered_functions = registered_functions
    
    return mock_server

# Utility functions for tests
@pytest.fixture
def assert_success_response():
    """Helper function to assert successful response format."""
    def _assert_success(response: Dict[str, Any]):
        assert isinstance(response, dict)
        assert response.get("status") == "success"
        assert "error" not in response
    return _assert_success

@pytest.fixture
def assert_error_response():
    """Helper function to assert error response format."""
    def _assert_error(response: Dict[str, Any], expected_error: str = None):
        assert isinstance(response, dict)
        assert response.get("status") == "error"
        assert "error" in response
        if expected_error:
            assert expected_error in response["error"]
    return _assert_error 