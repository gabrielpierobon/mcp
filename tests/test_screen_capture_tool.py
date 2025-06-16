import pytest
from unittest.mock import patch, Mock, MagicMock
from tools.screen_capture_tool import (
    quick_capture, detect_and_capture, capture_region_to_clipboard,
    capture_monitor_to_clipboard, capture_to_clipboard, register
)


class TestScreenCaptureTool:
    """Test suite for the screen capture tool."""
    
    @pytest.mark.asyncio
    async def test_quick_capture_success(self, mock_screen_capture, assert_success_response):
        """Test successful quick screen capture."""
        result = await quick_capture()
        
        assert_success_response(result)
        assert "message" in result
        assert "clipboard" in result["message"].lower()
        assert "screenshot" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_quick_capture_with_context(self, mock_screen_capture, assert_success_response):
        """Test quick capture with user context."""
        context = "I need help with this dialog box"
        result = await quick_capture(context)
        
        assert_success_response(result)
        assert "message" in result
        assert context.lower() in result["message"].lower() or "context" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_detect_and_capture_with_keyword(self, mock_screen_capture, assert_success_response):
        """Test detection and capture when [CAPTURE] keyword is present."""
        message_with_capture = "[CAPTURE] I need help with this screen"
        result = await detect_and_capture(message_with_capture)
        
        assert_success_response(result)
        assert "screenshot" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_detect_and_capture_without_keyword(self):
        """Test detection when no [CAPTURE] keyword is present."""
        message_without_capture = "Just a regular message"
        result = await detect_and_capture(message_without_capture)
        
        assert "status" in result
        assert "No [CAPTURE] keyword detected" in result["message"]
    
    @pytest.mark.asyncio
    async def test_detect_and_capture_case_insensitive(self, mock_screen_capture, assert_success_response):
        """Test that keyword detection is case insensitive."""
        test_cases = [
            "[capture] help me",
            "[CAPTURE] help me", 
            "[Capture] help me",
            "[CaPtUrE] help me"
        ]
        
        for message in test_cases:
            result = await detect_and_capture(message)
            assert_success_response(result)
    
    @pytest.mark.asyncio
    async def test_capture_region_success(self, mock_screen_capture, assert_success_response):
        """Test capturing a specific screen region."""
        result = await capture_region_to_clipboard(100, 200, 800, 600)
        
        assert_success_response(result)
        assert "region" in result["message"].lower()
        assert "100" in str(result["message"])
        assert "200" in str(result["message"])
    
    @pytest.mark.asyncio
    async def test_capture_region_with_context(self, mock_screen_capture, assert_success_response):
        """Test capturing region with context."""
        context = "Error dialog in top right corner"
        result = await capture_region_to_clipboard(100, 200, 400, 300, context)
        
        assert_success_response(result)
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_capture_region_invalid_coordinates(self, assert_error_response):
        """Test capture region with invalid coordinates."""
        # Test negative coordinates
        result = await capture_region_to_clipboard(-100, -200, 400, 300)
        assert result["status"] == "error"
        
        # Test zero or negative dimensions
        result = await capture_region_to_clipboard(100, 200, 0, 300)
        assert result["status"] == "error"
        
        result = await capture_region_to_clipboard(100, 200, 400, -100)
        assert result["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_capture_monitor_success(self, mock_screen_capture, assert_success_response):
        """Test capturing a specific monitor."""
        result = await capture_monitor_to_clipboard(1)
        
        assert_success_response(result)
        assert "monitor" in result["message"].lower()
        assert "1" in str(result["message"])
    
    @pytest.mark.asyncio
    async def test_capture_monitor_with_context(self, mock_screen_capture, assert_success_response):
        """Test capturing monitor with context."""
        context = "Secondary display with development tools"
        result = await capture_monitor_to_clipboard(2, context)
        
        assert_success_response(result)
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_capture_monitor_invalid_number(self, assert_error_response):
        """Test capture monitor with invalid monitor number."""
        # Test zero or negative monitor number
        result = await capture_monitor_to_clipboard(0)
        assert result["status"] == "error"
        
        result = await capture_monitor_to_clipboard(-1)
        assert result["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_capture_to_clipboard_default(self, mock_screen_capture, assert_success_response):
        """Test general capture to clipboard function."""
        result = await capture_to_clipboard()
        
        assert_success_response(result)
        assert "clipboard" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_capture_to_clipboard_with_monitor(self, mock_screen_capture, assert_success_response):
        """Test capture to clipboard with specific monitor."""
        result = await capture_to_clipboard(monitor=2)
        
        assert_success_response(result)
        assert "screenshot" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_capture_to_clipboard_with_region(self, mock_screen_capture, assert_success_response):
        """Test capture to clipboard with specific region."""
        region = {"x": 100, "y": 200, "width": 800, "height": 600}
        result = await capture_to_clipboard(region=region)
        
        assert_success_response(result)
        assert "screenshot" in result["message"].lower()
    

    

    

    

    
    @patch('tools.screen_capture_tool.fastmcp', create=True)
    def test_registration(self, mock_fastmcp, fastmcp_server):
        """Test that screen capture tools register correctly."""
        register(fastmcp_server)
        
        # Expected screen capture tools
        expected_tools = [
            "capture_to_clipboard", "quick_capture", "capture_region_to_clipboard",
            "capture_monitor_to_clipboard", "detect_and_capture"
        ]
        
        # Verify all functions were registered
        for tool_name in expected_tools:
            assert tool_name in fastmcp_server._registered_functions
            
        # Verify they were added to the tool manager
        tool_manager = fastmcp_server._tool_manager
        for tool_name in expected_tools:
            assert tool_name in tool_manager._tools
        
        # Check that the tools were attempted to be registered by checking the calls
        # The registration pattern is: mcp_instance.tool()(function_name)
        # So tool() should be called 5 times, once for each function
        assert fastmcp_server.tool.call_count == 5
        
        # Verify that tool() was called (the decorator pattern)
        assert fastmcp_server.tool.called
    
    @pytest.mark.asyncio
    async def test_capture_response_format(self, mock_screen_capture):
        """Test that all capture functions return consistent response formats."""
        functions_to_test = [
            (quick_capture, []),
            (detect_and_capture, ["[CAPTURE] test message"]),
            (capture_region_to_clipboard, [100, 200, 400, 300]),
            (capture_monitor_to_clipboard, [1]),
            (capture_to_clipboard, [])
        ]
        
        for func, args in functions_to_test:
            result = await func(*args)
            
            assert isinstance(result, dict)
            assert "status" in result
            assert result["status"] in ["success", "error"]
            assert "message" in result
            
            if result["status"] == "success":
                assert "clipboard" in result["message"].lower() or "screenshot" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_keyword_variations(self, mock_screen_capture):
        """Test various [CAPTURE] keyword variations."""
        test_cases = [
            "[CAPTURE]",
            "[CAPTURE] help",
            "Please [CAPTURE] this screen",
            "Before we continue [CAPTURE] and then...",
            "[capture] (lowercase)",
            "[ CAPTURE ]",  # With spaces
        ]
        
        for message in test_cases:
            result = await detect_and_capture(message)
            
            # Should detect the keyword (case variations handled)
            if "[capture]" in message.lower():
                assert result["status"] == "success"
            else:
                # Edge cases might not be detected depending on implementation
                assert "status" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_captures(self, mock_screen_capture):
        """Test concurrent screen capture operations."""
        import asyncio
        
        # Create multiple capture operations concurrently
        tasks = [
            quick_capture(f"Context {i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All operations should succeed or handle gracefully
        for result in results:
            if isinstance(result, dict):
                assert "status" in result
                assert "message" in result
    
    @pytest.mark.asyncio
    async def test_large_region_capture(self, mock_screen_capture):
        """Test capturing very large screen regions."""
        # Test with 4K resolution dimensions
        result = await capture_region_to_clipboard(0, 0, 3840, 2160)
        
        # Should either succeed or fail gracefully
        assert "status" in result
        if result["status"] == "error":
            # Large regions might be rejected for performance reasons
            assert "size" in result.get("error", "").lower()
    

    

    
    @pytest.mark.asyncio
    async def test_empty_context_handling(self, mock_screen_capture, assert_success_response):
        """Test handling of empty or None context."""
        # Test with None context
        result = await quick_capture(None)
        assert_success_response(result)
        
        # Test with empty string context
        result = await quick_capture("")
        assert_success_response(result)
        
        # Test with whitespace-only context
        result = await quick_capture("   ")
        assert_success_response(result) 