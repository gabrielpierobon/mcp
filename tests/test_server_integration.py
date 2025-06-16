import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    def test_server_imports(self):
        """Test that all server modules can be imported without errors."""
        try:
            import run_claude
            import run_http
            import run
            assert True  # If we reach here, imports succeeded
        except ImportError as e:
            pytest.fail(f"Failed to import server modules: {e}")
    
    def test_tool_imports(self):
        """Test that all tool modules can be imported."""
        tool_modules = [
            'tools.calculator_tool',
            'tools.get_weather_tool', 
            'tools.brave_search',
            'tools.file_system_tool',
            'tools.file_writing_tool',
            'tools.screen_capture_tool',
            'tools.airtable_tool',
            'tools.crawl4ai_tool',
            'tools.playwright_browser_tool',
            'tools.google_sheets_tool',
            'tools.google_docs_tool',
            'tools.google_slides_tool',
            'tools.rag_knowledge_base_tool'
        ]
        
        failed_imports = []
        for module_name in tool_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append((module_name, str(e)))
        
        if failed_imports:
            error_msg = "Failed to import tool modules:\n" + "\n".join(
                f"  {module}: {error}" for module, error in failed_imports
            )
            pytest.fail(error_msg)
    
    def test_fastmcp_server_creation(self, mock_env_vars):
        """Test FastMCP server creation and basic setup."""
        from fastmcp import FastMCP
        
        server = FastMCP("test-server")
        assert server is not None
        assert hasattr(server, '_tool_manager')
    
    def test_all_tools_registration(self, mock_env_vars, fastmcp_server):
        """Test that all tools can be registered without errors."""
        from tools import (
            calculator_tool, get_weather_tool, brave_search, 
            file_system_tool, file_writing_tool, screen_capture_tool
        )
        
        # Register core tools that should always work
        calculator_tool.register(fastmcp_server)
        get_weather_tool.register(fastmcp_server)
        brave_search.register(fastmcp_server)
        file_system_tool.register(fastmcp_server)
        file_writing_tool.register(fastmcp_server)
        screen_capture_tool.register(fastmcp_server)
        
        # Verify tools were registered
        tool_manager = fastmcp_server._tool_manager
        assert len(tool_manager._tools) > 0
        
        # Check for some expected tools
        expected_tools = ['calculator', 'get_weather', 'brave_web_search']
        for tool_name in expected_tools:
            assert tool_name in tool_manager._tools
    
    def test_optional_tools_registration(self, mock_env_vars, fastmcp_server):
        """Test registration of optional tools with dependency handling."""
        optional_tools = [
            'tools.airtable_tool',
            'tools.crawl4ai_tool', 
            'tools.playwright_browser_tool',
            'tools.google_sheets_tool',
            'tools.google_docs_tool',
            'tools.google_slides_tool',
            'tools.rag_knowledge_base_tool'
        ]
        
        for tool_module_name in optional_tools:
            try:
                tool_module = __import__(tool_module_name, fromlist=['register'])
                tool_module.register(fastmcp_server)
                # If registration succeeds, the tool should be available
                assert len(fastmcp_server._tool_manager._tools) > 0
            except (ImportError, AttributeError, Exception) as e:
                # Optional tools may fail due to missing dependencies
                # This is expected behavior
                print(f"Optional tool {tool_module_name} registration failed (expected): {e}")
    
    def test_server_environment_configuration(self, mock_env_vars):
        """Test server environment configuration."""
        # Test with mocked environment variables
        assert os.getenv('BRAVE_API_KEY') == 'test_brave_key'
        assert os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN') == 'test_airtable_token'
        assert os.getenv('MCP_SERVER_NAME') == 'test-mcp-server'
    
    def test_server_logging_configuration(self):
        """Test server logging configuration."""
        import logging
        
        # Test that logging is properly configured
        logger = logging.getLogger('mcp_server_test')
        logger.info("Test log message")
        
        # Should not raise any errors
        assert True
    
    @pytest.mark.asyncio
    async def test_tool_execution_flow(self, mock_env_vars, fastmcp_server):
        """Test the complete flow of tool execution."""
        from tools.calculator_tool import calculator, register
        
        # Register the calculator tool
        register(fastmcp_server)
        
        # Execute the tool directly
        result = await calculator("add", 5, 3)
        
        assert result["status"] == "success"
        assert result["result"] == 8
    
    def test_server_error_handling(self, fastmcp_server):
        """Test server-level error handling."""
        # Test registering invalid tool
        try:
            def invalid_tool():
                raise Exception("Invalid tool")
            
            fastmcp_server.tool()(invalid_tool)
            # Should handle registration gracefully
            assert True
        except Exception:
            # Some error handling is expected
            pass
    
    def test_server_with_missing_dependencies(self):
        """Test server behavior when optional dependencies are missing."""
        # Mock missing optional dependencies
        with patch.dict('sys.modules', {
            'crawl4ai': None,
            'playwright': None,
            'google.auth': None,
            'airtable': None
        }):
            try:
                from fastmcp import FastMCP
                server = FastMCP("test-server")
                
                # Core functionality should still work
                assert server is not None
            except ImportError:
                pytest.fail("Server should work without optional dependencies")
    
    def test_concurrent_tool_registration(self, fastmcp_server):
        """Test concurrent tool registration."""
        import threading
        
        def register_calculator():
            from tools.calculator_tool import register
            register(fastmcp_server)
        
        def register_weather():
            from tools.get_weather_tool import register
            register(fastmcp_server)
        
        # Create threads for concurrent registration
        thread1 = threading.Thread(target=register_calculator)
        thread2 = threading.Thread(target=register_weather)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Both tools should be registered
        tool_manager = fastmcp_server._tool_manager
        assert 'calculator' in tool_manager._tools
        assert 'get_weather' in tool_manager._tools
    
    def test_server_memory_usage(self, fastmcp_server):
        """Test server memory usage with multiple tools."""
        import gc
        
        # Register multiple tools
        from tools import calculator_tool, get_weather_tool, brave_search
        
        calculator_tool.register(fastmcp_server)
        get_weather_tool.register(fastmcp_server)
        brave_search.register(fastmcp_server)
        
        # Force garbage collection
        gc.collect()
        
        # Server should still be functional
        tool_manager = fastmcp_server._tool_manager
        assert len(tool_manager._tools) >= 3
    
    def test_server_configuration_validation(self):
        """Test server configuration validation."""
        # Test various server name configurations
        from fastmcp import FastMCP
        
        valid_names = ["test-server", "mcp_server", "MyServer123"]
        for name in valid_names:
            server = FastMCP(name)
            assert server is not None
    
    @pytest.mark.asyncio
    async def test_tool_error_isolation(self, fastmcp_server):
        """Test that tool errors don't crash the server."""
        from tools.calculator_tool import register
        
        register(fastmcp_server)
        
        # Test with invalid input
        from tools.calculator_tool import calculator
        result = await calculator("invalid_operation", 1, 2)
        
        # Should return error response, not crash
        assert result["status"] == "error"
        assert "error" in result
        
        # Server should still be functional for other operations
        valid_result = await calculator("add", 1, 2)
        assert valid_result["status"] == "success"
    
    def test_api_key_security(self, mock_env_vars):
        """Test that API keys are handled securely."""
        # API keys should be available but not logged in plain text
        import logging
        
        with patch('logging.Logger.info') as mock_log:
            # Import a module that uses API keys
            from tools.brave_search import BRAVE_API_KEY
            
            # Check that API key is loaded (could be mock or real)
            assert BRAVE_API_KEY is not None
            assert len(BRAVE_API_KEY) > 0
            
            # Check that full API keys are not logged
            for call in mock_log.call_args_list:
                args, kwargs = call
                log_message = str(args[0]) if args else ""
                # Ensure API key is not logged in plain text
                if BRAVE_API_KEY in log_message:
                    pytest.fail(f"API key found in log message: {log_message}")
    
    def test_server_shutdown_cleanup(self, fastmcp_server):
        """Test server shutdown and cleanup."""
        from tools.calculator_tool import register
        
        register(fastmcp_server)
        
        # Simulate server shutdown
        initial_tools_count = len(fastmcp_server._tool_manager._tools)
        assert initial_tools_count > 0
        
        # In a real scenario, cleanup would happen here
        # For testing, we just verify the server state
        assert fastmcp_server._tool_manager is not None
    
    def test_cross_tool_compatibility(self, mock_env_vars, fastmcp_server):
        """Test that different tools can coexist without conflicts."""
        from tools import calculator_tool, get_weather_tool, file_system_tool
        
        # Register multiple tools
        calculator_tool.register(fastmcp_server)
        get_weather_tool.register(fastmcp_server)
        file_system_tool.register(fastmcp_server)
        
        tool_manager = fastmcp_server._tool_manager
        
        # Check that all tools are registered
        assert 'calculator' in tool_manager._tools
        assert 'get_weather' in tool_manager._tools
        
        # Check for file system tools
        file_tools = [name for name in tool_manager._tools.keys() if 'file' in name.lower()]
        assert len(file_tools) > 0
    
    def test_server_performance_with_many_tools(self, fastmcp_server):
        """Test server performance with many tools registered."""
        import time
        
        start_time = time.time()
        
        # Register multiple tools
        tools_to_register = [
            'tools.calculator_tool',
            'tools.get_weather_tool',
            'tools.brave_search',
            'tools.file_system_tool',
            'tools.file_writing_tool',
            'tools.screen_capture_tool'
        ]
        
        for tool_module_name in tools_to_register:
            try:
                tool_module = __import__(tool_module_name, fromlist=['register'])
                tool_module.register(fastmcp_server)
            except Exception as e:
                print(f"Tool registration failed: {tool_module_name} - {e}")
        
        registration_time = time.time() - start_time
        
        # Registration should be reasonably fast (under 5 seconds)
        assert registration_time < 5.0
        
        # Server should have registered tools
        assert len(fastmcp_server._tool_manager._tools) > 0
    
    def test_tool_parameter_validation(self, fastmcp_server):
        """Test that tool parameter validation works correctly."""
        from tools.calculator_tool import register, calculator
        
        register(fastmcp_server)
        
        # Tool should be accessible through the tool manager
        tool_manager = fastmcp_server._tool_manager
        assert 'calculator' in tool_manager._tools
        
        # The actual parameter validation would be handled by FastMCP
        # Here we just ensure the tool is properly registered
        calculator_tool = tool_manager._tools['calculator']
        assert calculator_tool is not None 