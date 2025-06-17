# tests/test_playwright_browser_tool.py
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from tools.playwright_browser_tool import (
    launch_browser,
    navigate_to_page,
    get_page_content,
    click_element,
    fill_form_field,
    wait_for_element,
    execute_javascript,
    get_accessibility_snapshot,
    close_browser_context,
    list_browser_contexts
)

@pytest.mark.unit
@pytest.mark.external_api
class TestPlaywrightBrowserTool:
    """Test suite for Playwright browser automation tool."""
    
    @pytest.fixture
    def mock_playwright_available(self):
        """Mock Playwright as available for testing."""
        with patch('tools.playwright_browser_tool.PLAYWRIGHT_AVAILABLE', True):
            yield
    
    @pytest.fixture
    def mock_playwright_unavailable(self):
        """Mock Playwright as unavailable for testing."""
        with patch('tools.playwright_browser_tool.PLAYWRIGHT_AVAILABLE', False):
            yield
    
    @pytest.fixture
    def mock_playwright_components(self):
        """Mock all Playwright components."""
        # Mock page
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.goto = AsyncMock(return_value=Mock(status=200))
        mock_page.content = AsyncMock(return_value="<html><body><h1>Test Page</h1></body></html>")
        mock_page.text_content = AsyncMock(return_value="Test Page")
        mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
        mock_page.click = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Element text")
        mock_element.inner_html = AsyncMock(return_value="<span>Element HTML</span>")
        mock_page.query_selector = AsyncMock(return_value=mock_element)
        mock_page.evaluate = AsyncMock(return_value="JS result")
        mock_accessibility = Mock()
        mock_accessibility.snapshot = AsyncMock(return_value={"role": "RootWebArea", "name": "Test Page"})
        mock_page.accessibility = mock_accessibility
        
        # Mock context
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()
        
        # Mock browser
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        
        # Mock browser launchers
        mock_chromium = Mock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)
        mock_firefox = Mock()
        mock_firefox.launch = AsyncMock(return_value=mock_browser)
        mock_webkit = Mock()
        mock_webkit.launch = AsyncMock(return_value=mock_browser)
        
        # Mock playwright instance
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium = mock_chromium
        mock_playwright_instance.firefox = mock_firefox
        mock_playwright_instance.webkit = mock_webkit
        mock_playwright_instance.stop = AsyncMock()
        
        # Mock async_playwright function
        async def mock_async_playwright_func():
            return mock_playwright_instance
        
        # Mock async_playwright class
        mock_async_playwright = Mock()
        mock_async_playwright.start = AsyncMock(return_value=mock_playwright_instance)
        
        return {
            'async_playwright': mock_async_playwright,
            'playwright_instance': mock_playwright_instance,
            'browser': mock_browser,
            'context': mock_context,
            'page': mock_page,
            'element': mock_element
        }
    
    @pytest.fixture
    def setup_mocks(self, mock_playwright_available, mock_playwright_components):
        """Setup comprehensive mocks for Playwright."""
        import tools.playwright_browser_tool
        
        # Create a mock function that returns the mock async_playwright object
        def mock_async_playwright_func():
            return mock_playwright_components['async_playwright']
        
        # Mock the async_playwright import
        setattr(tools.playwright_browser_tool, 'async_playwright', mock_async_playwright_func)
        
        yield mock_playwright_components
        
        # Clean up browser contexts
        tools.playwright_browser_tool._browser_contexts.clear()
        tools.playwright_browser_tool._active_pages.clear()

@pytest.mark.unit
@pytest.mark.external_api 
class TestLaunchBrowser(TestPlaywrightBrowserTool):
    """Test launch_browser function."""
    
    @pytest.mark.asyncio
    async def test_launch_browser_success_chromium(self, setup_mocks):
        """Test successful browser launch with Chromium."""
        result = await launch_browser()
        
        assert result["status"] == "success"
        assert result["context_id"] == "default"
        assert result["browser_type"] == "chromium"
        assert result["headless"] is True
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_launch_browser_success_firefox(self, setup_mocks):
        """Test successful browser launch with Firefox."""
        result = await launch_browser(browser_type="firefox", headless=False, context_id="test_context")
        
        assert result["status"] == "success"
        assert result["context_id"] == "test_context"
        assert result["browser_type"] == "firefox"
        assert result["headless"] is False
    
    @pytest.mark.asyncio
    async def test_launch_browser_success_webkit(self, setup_mocks):
        """Test successful browser launch with WebKit."""
        result = await launch_browser(browser_type="webkit")
        
        assert result["status"] == "success"
        assert result["browser_type"] == "webkit"
    
    @pytest.mark.asyncio
    async def test_launch_browser_existing_context(self, setup_mocks):
        """Test launching browser with existing context."""
        # First launch
        await launch_browser(context_id="existing")
        
        # Second launch with same context_id
        result = await launch_browser(context_id="existing")
        
        assert result["status"] == "success"
        assert "already exists" in result["message"]
    
    @pytest.mark.asyncio
    async def test_launch_browser_playwright_unavailable(self, mock_playwright_unavailable):
        """Test browser launch when Playwright is not available."""
        result = await launch_browser()
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_launch_browser_exception_handling(self, setup_mocks):
        """Test browser launch exception handling."""
        # Make browser launch fail
        setup_mocks['playwright_instance'].chromium.launch.side_effect = Exception("Launch failed")
        
        result = await launch_browser()
        
        assert result["status"] == "error"
        assert "Failed to launch browser" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestNavigateToPage(TestPlaywrightBrowserTool):
    """Test navigate_to_page function."""
    
    @pytest.mark.asyncio
    async def test_navigate_to_page_success(self, setup_mocks):
        """Test successful page navigation."""
        # Launch browser first
        await launch_browser()
        
        result = await navigate_to_page("https://example.com")
        
        assert result["status"] == "success"
        assert result["url"] == "https://example.com"
        assert result["title"] == "Test Page"
        assert result["status_code"] == 200
        assert result["context_id"] == "default"
    
    @pytest.mark.asyncio
    async def test_navigate_to_page_auto_launch(self, setup_mocks):
        """Test navigation with automatic browser launch."""
        result = await navigate_to_page("https://example.com", context_id="auto_launch")
        
        assert result["status"] == "success"
        assert result["context_id"] == "auto_launch"
    
    @pytest.mark.asyncio
    async def test_navigate_to_page_custom_parameters(self, setup_mocks):
        """Test navigation with custom parameters."""
        await launch_browser(context_id="custom")
        
        result = await navigate_to_page(
            "https://example.com", 
            context_id="custom",
            wait_for_load_state="load",
            timeout=60000
        )
        
        assert result["status"] == "success"
        assert result["wait_for_load_state"] == "load"
    
    @pytest.mark.asyncio
    async def test_navigate_to_page_playwright_unavailable(self, mock_playwright_unavailable):
        """Test navigation when Playwright is not available."""
        result = await navigate_to_page("https://example.com")
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_navigate_to_page_exception_handling(self, setup_mocks):
        """Test navigation exception handling."""
        await launch_browser()
        
        # Make navigation fail
        setup_mocks['page'].goto.side_effect = Exception("Navigation failed")
        
        result = await navigate_to_page("https://example.com")
        
        assert result["status"] == "error"
        assert "Navigation failed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestGetPageContent(TestPlaywrightBrowserTool):
    """Test get_page_content function."""
    
    @pytest.mark.asyncio
    async def test_get_page_content_text(self, setup_mocks):
        """Test getting page content as text."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_page_content(content_type="text")
        
        assert result["status"] == "success"
        assert result["content_type"] == "text"
        assert result["content"] == "Test Page"
        assert result["url"] == "https://example.com"
        assert result["title"] == "Test Page"
    
    @pytest.mark.asyncio
    async def test_get_page_content_html(self, setup_mocks):
        """Test getting page content as HTML."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_page_content(content_type="html")
        
        assert result["status"] == "success"
        assert result["content_type"] == "html"
        assert "<html>" in result["content"]
    
    @pytest.mark.asyncio
    async def test_get_page_content_markdown(self, setup_mocks):
        """Test getting page content as markdown."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_page_content(content_type="markdown")
        
        assert result["status"] == "success"
        assert result["content_type"] == "markdown"
        assert result["content"].startswith("# Test Page")
    
    @pytest.mark.asyncio
    async def test_get_page_content_screenshot(self, setup_mocks):
        """Test taking page screenshot."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_page_content(content_type="screenshot")
        
        assert result["status"] == "success"
        assert result["content_type"] == "screenshot"
        assert "screenshot_base64" in result
        assert result["url"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_get_page_content_with_selector(self, setup_mocks):
        """Test getting content from specific element."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Mock element
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Element text"
        mock_element.inner_html.return_value = "<span>Element HTML</span>"
        setup_mocks['page'].wait_for_selector.return_value = mock_element
        
        result = await get_page_content(content_type="text", selector="h1")
        
        assert result["status"] == "success"
        assert result["content"] == "Element text"
        assert result["selector"] == "h1"
    
    @pytest.mark.asyncio
    async def test_get_page_content_no_active_page(self, setup_mocks):
        """Test getting content when no page is active."""
        result = await get_page_content()
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_page_content_playwright_unavailable(self, mock_playwright_unavailable):
        """Test getting content when Playwright is not available."""
        result = await get_page_content()
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestClickElement(TestPlaywrightBrowserTool):
    """Test click_element function."""
    
    @pytest.mark.asyncio
    async def test_click_element_success(self, setup_mocks):
        """Test successful element clicking."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await click_element("button")
        
        assert result["status"] == "success"
        assert result["selector"] == "button"
        assert result["context_id"] == "default"
        assert result["url"] == "https://example.com"
        assert result["wait_for_navigation"] is False
        setup_mocks['page'].click.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_click_element_with_navigation(self, setup_mocks):
        """Test clicking element with navigation wait."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Mock expect_navigation
        setup_mocks['page'].expect_navigation = Mock()
        setup_mocks['page'].expect_navigation.return_value.__aenter__ = AsyncMock()
        setup_mocks['page'].expect_navigation.return_value.__aexit__ = AsyncMock()
        
        result = await click_element("a", wait_for_navigation=True, timeout=15000)
        
        assert result["status"] == "success"
        assert result["wait_for_navigation"] is True
    
    @pytest.mark.asyncio
    async def test_click_element_no_active_page(self, setup_mocks):
        """Test clicking element when no page is active."""
        result = await click_element("button")
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_click_element_playwright_unavailable(self, mock_playwright_unavailable):
        """Test clicking element when Playwright is not available."""
        result = await click_element("button")
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_click_element_exception_handling(self, setup_mocks):
        """Test click element exception handling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Make click fail
        setup_mocks['page'].click.side_effect = Exception("Click failed")
        
        result = await click_element("button")
        
        assert result["status"] == "error"
        assert "Failed to click element" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestFillFormField(TestPlaywrightBrowserTool):
    """Test fill_form_field function."""
    
    @pytest.mark.asyncio
    async def test_fill_form_field_success(self, setup_mocks):
        """Test successful form field filling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await fill_form_field("input[name='username']", "test_user")
        
        assert result["status"] == "success"
        assert result["selector"] == "input[name='username']"
        assert result["value"] == "test_user"
        assert result["clear_first"] is True
        assert result["url"] == "https://example.com"
        setup_mocks['page'].fill.assert_called()
    
    @pytest.mark.asyncio
    async def test_fill_form_field_no_clear(self, setup_mocks):
        """Test form field filling without clearing first."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await fill_form_field("input", "value", clear_first=False, timeout=15000)
        
        assert result["status"] == "success"
        assert result["clear_first"] is False
    
    @pytest.mark.asyncio
    async def test_fill_form_field_no_active_page(self, setup_mocks):
        """Test filling form field when no page is active."""
        result = await fill_form_field("input", "value")
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fill_form_field_playwright_unavailable(self, mock_playwright_unavailable):
        """Test filling form field when Playwright is not available."""
        result = await fill_form_field("input", "value")
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fill_form_field_exception_handling(self, setup_mocks):
        """Test fill form field exception handling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Make fill fail
        setup_mocks['page'].fill.side_effect = Exception("Fill failed")
        
        result = await fill_form_field("input", "value")
        
        assert result["status"] == "error"
        assert "Failed to fill form field" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestWaitForElement(TestPlaywrightBrowserTool):
    """Test wait_for_element function."""
    
    @pytest.mark.asyncio
    async def test_wait_for_element_success(self, setup_mocks):
        """Test successful element waiting."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await wait_for_element("div.loading")
        
        assert result["status"] == "success"
        assert result["selector"] == "div.loading"
        assert result["state"] == "visible"
        assert result["element_text"] == "Element text"
        assert result["context_id"] == "default"
        assert result["url"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_wait_for_element_custom_state(self, setup_mocks):
        """Test waiting for element with custom state."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await wait_for_element("div", state="hidden", timeout=15000)
        
        assert result["status"] == "success"
        assert result["state"] == "hidden"
    
    @pytest.mark.asyncio
    async def test_wait_for_element_no_active_page(self, setup_mocks):
        """Test waiting for element when no page is active."""
        result = await wait_for_element("div")
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_wait_for_element_playwright_unavailable(self, mock_playwright_unavailable):
        """Test waiting for element when Playwright is not available."""
        result = await wait_for_element("div")
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_wait_for_element_exception_handling(self, setup_mocks):
        """Test wait for element exception handling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Make wait fail
        setup_mocks['page'].wait_for_selector.side_effect = Exception("Wait failed")
        
        result = await wait_for_element("div")
        
        assert result["status"] == "error"
        assert "Failed to wait for element" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestExecuteJavaScript(TestPlaywrightBrowserTool):
    """Test execute_javascript function."""
    
    @pytest.mark.asyncio
    async def test_execute_javascript_success(self, setup_mocks):
        """Test successful JavaScript execution."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await execute_javascript("document.title")
        
        assert result["status"] == "success"
        assert result["script"] == "document.title"
        assert result["result"] == "JS result"
        assert result["context_id"] == "default"
        assert result["url"] == "https://example.com"
        setup_mocks['page'].evaluate.assert_called_once_with("document.title")
    
    @pytest.mark.asyncio
    async def test_execute_javascript_complex_script(self, setup_mocks):
        """Test executing complex JavaScript."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        script = "return Array.from(document.querySelectorAll('a')).map(a => a.href)"
        result = await execute_javascript(script)
        
        assert result["status"] == "success"
        assert result["script"] == script
    
    @pytest.mark.asyncio
    async def test_execute_javascript_no_active_page(self, setup_mocks):
        """Test executing JavaScript when no page is active."""
        result = await execute_javascript("document.title")
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_javascript_playwright_unavailable(self, mock_playwright_unavailable):
        """Test executing JavaScript when Playwright is not available."""
        result = await execute_javascript("document.title")
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_javascript_exception_handling(self, setup_mocks):
        """Test JavaScript execution exception handling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Make execution fail
        setup_mocks['page'].evaluate.side_effect = Exception("JS execution failed")
        
        result = await execute_javascript("invalid.script()")
        
        assert result["status"] == "error"
        assert "Failed to execute JavaScript" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestGetAccessibilitySnapshot(TestPlaywrightBrowserTool):
    """Test get_accessibility_snapshot function."""
    
    @pytest.mark.asyncio
    async def test_get_accessibility_snapshot_success(self, setup_mocks):
        """Test successful accessibility snapshot."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_accessibility_snapshot()
        
        assert result["status"] == "success"
        assert "accessibility_tree" in result
        assert result["accessibility_tree"]["role"] == "RootWebArea"
        assert result["context_id"] == "default"
        assert result["url"] == "https://example.com"
        assert result["title"] == "Test Page"
        assert result["interesting_only"] is True
    
    @pytest.mark.asyncio
    async def test_get_accessibility_snapshot_all_elements(self, setup_mocks):
        """Test accessibility snapshot with all elements."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        result = await get_accessibility_snapshot(interesting_only=False)
        
        assert result["status"] == "success"
        assert result["interesting_only"] is False
    
    @pytest.mark.asyncio
    async def test_get_accessibility_snapshot_no_active_page(self, setup_mocks):
        """Test accessibility snapshot when no page is active."""
        result = await get_accessibility_snapshot()
        
        assert result["status"] == "error"
        assert "No active page" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_accessibility_snapshot_playwright_unavailable(self, mock_playwright_unavailable):
        """Test accessibility snapshot when Playwright is not available."""
        result = await get_accessibility_snapshot()
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_accessibility_snapshot_exception_handling(self, setup_mocks):
        """Test accessibility snapshot exception handling."""
        await launch_browser()
        await navigate_to_page("https://example.com")
        
        # Make snapshot fail
        setup_mocks['page'].accessibility.snapshot.side_effect = Exception("Snapshot failed")
        
        result = await get_accessibility_snapshot()
        
        assert result["status"] == "error"
        assert "Failed to get accessibility snapshot" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestCloseBrowserContext(TestPlaywrightBrowserTool):
    """Test close_browser_context function."""
    
    @pytest.mark.asyncio
    async def test_close_browser_context_success(self, setup_mocks):
        """Test successful browser context closing."""
        # Launch browser first
        await launch_browser(context_id="test_close")
        await navigate_to_page("https://example.com", context_id="test_close")
        
        result = await close_browser_context("test_close")
        
        assert result["status"] == "success"
        assert result["context_id"] == "test_close"
        assert "closed successfully" in result["message"]
        
        # Verify cleanup
        setup_mocks['context'].close.assert_called_once()
        setup_mocks['browser'].close.assert_called_once()
        setup_mocks['playwright_instance'].stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_browser_context_not_found(self, setup_mocks):
        """Test closing non-existent browser context."""
        result = await close_browser_context("non_existent")
        
        assert result["status"] == "success"
        assert "not found or already closed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_close_browser_context_playwright_unavailable(self, mock_playwright_unavailable):
        """Test closing browser context when Playwright is not available."""
        result = await close_browser_context()
        
        assert result["status"] == "error"
        assert "Playwright is not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_close_browser_context_exception_handling(self, setup_mocks):
        """Test close browser context exception handling."""
        await launch_browser(context_id="error_test")
        
        # Make close fail
        setup_mocks['context'].close.side_effect = Exception("Close failed")
        
        result = await close_browser_context("error_test")
        
        assert result["status"] == "error"
        assert "Failed to close browser context" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestListBrowserContexts(TestPlaywrightBrowserTool):
    """Test list_browser_contexts function."""
    
    @pytest.mark.asyncio
    async def test_list_browser_contexts_empty(self, setup_mocks):
        """Test listing browser contexts when none exist."""
        result = await list_browser_contexts()
        
        assert result["status"] == "success"
        assert result["active_contexts"] == []
        assert result["total_contexts"] == 0
    
    @pytest.mark.asyncio
    async def test_list_browser_contexts_with_contexts(self, setup_mocks):
        """Test listing browser contexts with active contexts."""
        # Launch multiple browsers
        await launch_browser(context_id="context1")
        await launch_browser(context_id="context2")
        await navigate_to_page("https://example1.com", context_id="context1")
        await navigate_to_page("https://example2.com", context_id="context2")
        
        result = await list_browser_contexts()
        
        assert result["status"] == "success"
        assert result["total_contexts"] == 2
        assert len(result["active_contexts"]) == 2
        
        # Check context details
        context_ids = [ctx["context_id"] for ctx in result["active_contexts"]]
        assert "context1" in context_ids
        assert "context2" in context_ids
        
        # Check that contexts have active pages
        for ctx in result["active_contexts"]:
            assert ctx["has_active_page"] is True
            assert ctx["current_url"] is not None
            assert ctx["current_title"] is not None
    
    @pytest.mark.asyncio
    async def test_list_browser_contexts_mixed_states(self, setup_mocks):
        """Test listing contexts with mixed active/inactive page states."""
        await launch_browser(context_id="with_page")
        await launch_browser(context_id="without_page")
        await navigate_to_page("https://example.com", context_id="with_page")
        
        result = await list_browser_contexts()
        
        assert result["status"] == "success"
        assert result["total_contexts"] == 2
        
        # Find contexts
        with_page_ctx = next(ctx for ctx in result["active_contexts"] if ctx["context_id"] == "with_page")
        without_page_ctx = next(ctx for ctx in result["active_contexts"] if ctx["context_id"] == "without_page")
        
        assert with_page_ctx["has_active_page"] is True
        assert without_page_ctx["has_active_page"] is False

@pytest.mark.integration
class TestPlaywrightBrowserToolRegistration:
    """Test tool registration."""
    
    def test_tool_registration_available(self):
        """Test tool registration when Playwright is available."""
        mock_mcp = Mock()
        mock_tool = Mock()
        mock_mcp.tool.return_value = mock_tool
        
        with patch('tools.playwright_browser_tool.PLAYWRIGHT_AVAILABLE', True):
            from tools.playwright_browser_tool import register
            register(mock_mcp)
        
        # Should register all 10 tools
        assert mock_mcp.tool.call_count == 10
    
    def test_tool_registration_unavailable(self):
        """Test tool registration when Playwright is not available."""
        mock_mcp = Mock()
        
        with patch('tools.playwright_browser_tool.PLAYWRIGHT_AVAILABLE', False):
            from tools.playwright_browser_tool import register
            register(mock_mcp)
        
        # Should not register any tools
        mock_mcp.tool.assert_not_called()

@pytest.mark.unit
class TestErrorHandling(TestPlaywrightBrowserTool):
    """Test comprehensive error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_complex_workflow_success(self, setup_mocks):
        """Test a complex workflow with multiple operations."""
        # Launch browser
        launch_result = await launch_browser(context_id="workflow")
        assert launch_result["status"] == "success"
        
        # Navigate to page
        nav_result = await navigate_to_page("https://example.com", context_id="workflow")
        assert nav_result["status"] == "success"
        
        # Get page content
        content_result = await get_page_content(context_id="workflow")
        assert content_result["status"] == "success"
        
        # Click element
        click_result = await click_element("button", context_id="workflow")
        assert click_result["status"] == "success"
        
        # Fill form
        fill_result = await fill_form_field("input", "test", context_id="workflow")
        assert fill_result["status"] == "success"
        
        # Execute JavaScript
        js_result = await execute_javascript("document.title", context_id="workflow")
        assert js_result["status"] == "success"
        
        # Get accessibility tree
        a11y_result = await get_accessibility_snapshot(context_id="workflow")
        assert a11y_result["status"] == "success"
        
        # List contexts
        list_result = await list_browser_contexts()
        assert list_result["status"] == "success"
        assert list_result["total_contexts"] == 1
        
        # Close context
        close_result = await close_browser_context("workflow")
        assert close_result["status"] == "success"
        
        # Verify context is closed
        final_list = await list_browser_contexts()
        assert final_list["total_contexts"] == 0
    
    @pytest.mark.asyncio
    async def test_context_isolation(self, setup_mocks):
        """Test that contexts are properly isolated."""
        # Launch two contexts
        await launch_browser(context_id="context_a")
        await launch_browser(context_id="context_b")
        
        # Navigate to different pages
        await navigate_to_page("https://site-a.com", context_id="context_a")
        await navigate_to_page("https://site-b.com", context_id="context_b")
        
        # Get content from each context
        content_a = await get_page_content(context_id="context_a")
        content_b = await get_page_content(context_id="context_b")
        
        assert content_a["status"] == "success"
        assert content_b["status"] == "success"
        
        # Each context should maintain its own state
        assert content_a["url"] == "https://example.com"  # Mock returns this URL
        assert content_b["url"] == "https://example.com"  # Mock returns this URL
        
        # Close one context
        await close_browser_context("context_a")
        
        # Other context should still work
        remaining_content = await get_page_content(context_id="context_b")
        assert remaining_content["status"] == "success"
        
        # First context should be gone
        result = await get_page_content(context_id="context_a")
        assert result["status"] == "error" 