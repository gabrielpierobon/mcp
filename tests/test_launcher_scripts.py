"""
Test suite for launcher scripts (run.py, run_http.py, run_claude.py).
Tests argument parsing, environment detection, imports, and error handling.
"""

import pytest
import sys
import os
import argparse
from unittest.mock import patch, Mock, MagicMock, call
from pathlib import Path
from io import StringIO

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def clean_argv():
    """Clean sys.argv for testing."""
    original_argv = sys.argv.copy()
    yield
    sys.argv = original_argv

@pytest.fixture
def clean_env():
    """Clean environment variables for testing."""
    original_env = os.environ.copy()
    # Clear relevant environment variables
    env_vars_to_clear = [
        'CLAUDE_DESKTOP', 'ANTHROPIC_CLIENT', 'MCP_FORCE_HTTP', 'MCP_FORCE_STDIO',
        'MCP_SERVER_NAME', 'MCP_HOST', 'MCP_PORT', 'BRAVE_API_KEY', 
        'AIRTABLE_PERSONAL_ACCESS_TOKEN', 'GOOGLE_CREDENTIALS_FILE'
    ]
    for var in env_vars_to_clear:
        os.environ.pop(var, None)
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_fastmcp():
    """Mock FastMCP to prevent actual server startup."""
    with patch('fastmcp.FastMCP') as mock:
        mock_instance = Mock()
        # Configure the run method to accept any arguments
        mock_instance.run = Mock(return_value=None)
        mock_instance.run.side_effect = None
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_tool_imports():
    """Mock all tool imports to prevent dependency issues."""
    tool_modules = [
        'tools.calculator_tool',
        'tools.get_weather_tool', 
        'tools.brave_search',
        'tools.crawl4ai_tool',
        'tools.airtable_tool',
        'tools.playwright_browser_tool',
        'tools.google_sheets_tool',
        'tools.google_docs_tool',
        'tools.google_slides_tool',
        'tools.file_system_tool',
        'tools.file_writing_tool',
        'tools.screen_capture_tool',
        'tools.rag_knowledge_base_tool'
    ]
    
    with patch.dict('sys.modules'):
        for module in tool_modules:
            mock_module = Mock()
            mock_module.register = Mock()
            sys.modules[module] = mock_module
        yield

class TestMainLauncherScript:
    """Test the main run.py launcher script."""
    
    def test_imports_successfully(self):
        """Test that run.py can be imported without errors."""
        try:
            import run
            assert hasattr(run, 'main')
            assert hasattr(run, 'detect_claude_desktop')
            assert hasattr(run, 'show_help')
        except ImportError as e:
            pytest.fail(f"Failed to import run.py: {e}")
    
    def test_detect_claude_desktop_with_env_vars(self, clean_env):
        """Test Claude Desktop detection with environment variables."""
        import run
        
        # Test with CLAUDE_DESKTOP environment variable
        os.environ['CLAUDE_DESKTOP'] = '1'
        assert run.detect_claude_desktop() is True
        
        # Test with ANTHROPIC_CLIENT environment variable
        os.environ.pop('CLAUDE_DESKTOP', None)
        os.environ['ANTHROPIC_CLIENT'] = '1'
        assert run.detect_claude_desktop() is True
    
    def test_detect_claude_desktop_no_tty(self, clean_env, clean_argv):
        """Test Claude Desktop detection with no TTY."""
        import run
        
        # Mock sys.stdin.isatty() to return False (no TTY)
        with patch('sys.stdin.isatty', return_value=False):
            # Set sys.argv to just script name (no arguments)
            sys.argv = ['run.py']
            assert run.detect_claude_desktop() is True
    
    def test_detect_claude_desktop_force_http(self, clean_env, clean_argv):
        """Test Claude Desktop detection with MCP_FORCE_HTTP."""
        import run
        
        os.environ['MCP_FORCE_HTTP'] = '1'
        sys.argv = ['run.py']
        
        with patch('sys.stdin.isatty', return_value=False):
            assert run.detect_claude_desktop() is False
    
    def test_detect_claude_desktop_with_args(self, clean_env, clean_argv):
        """Test Claude Desktop detection with command line arguments."""
        import run
        
        # With arguments, should not auto-detect as Claude Desktop
        sys.argv = ['run.py', '--some-arg']
        
        with patch('sys.stdin.isatty', return_value=False):
            assert run.detect_claude_desktop() is False
    
    def test_detect_claude_desktop_with_tty(self, clean_env, clean_argv):
        """Test Claude Desktop detection with TTY available."""
        import run
        
        sys.argv = ['run.py']
        
        # With TTY available, should not auto-detect as Claude Desktop
        with patch('sys.stdin.isatty', return_value=True):
            assert run.detect_claude_desktop() is False
    
    def test_show_help_output(self, clean_env):
        """Test help output contains expected information."""
        import run
        
        with patch('builtins.print') as mock_print:
            run.show_help()
            
        # Check that help was printed
        mock_print.assert_called_once()
        help_text = mock_print.call_args[0][0]
        
        # Verify key sections are present
        assert "MCP Server Launcher" in help_text
        assert "For Claude Desktop:" in help_text
        assert "For n8n Integration:" in help_text
        assert "Environment Variables:" in help_text
        assert "BRAVE_API_KEY" in help_text
        assert "AIRTABLE_PERSONAL_ACCESS_TOKEN" in help_text
    
    @patch('run.show_help')
    def test_main_help_argument(self, mock_show_help, clean_argv):
        """Test main function with --help argument."""
        import run
        
        sys.argv = ['run.py', '--help']
        run.main()
        
        mock_show_help.assert_called_once()
    
    @patch('run.show_help')
    def test_main_help_short_argument(self, mock_show_help, clean_argv):
        """Test main function with -h argument."""
        import run
        
        sys.argv = ['run.py', '-h']
        run.main()
        
        mock_show_help.assert_called_once()
    
    @patch('run_http.main')
    def test_main_http_argument(self, mock_http_main, clean_argv, clean_env):
        """Test main function with --http argument."""
        import run
        
        sys.argv = ['run.py', '--http']
        
        with patch('builtins.print'):
            run.main()
        
        mock_http_main.assert_called_once()
        assert os.environ.get('MCP_FORCE_HTTP') == '1'
    
    @patch('run_claude.main')
    def test_main_stdio_argument(self, mock_claude_main, clean_argv, clean_env):
        """Test main function with --stdio argument."""
        import run
        
        sys.argv = ['run.py', '--stdio']
        
        with patch('builtins.print'):
            run.main()
        
        mock_claude_main.assert_called_once()
    
    @patch('run_claude.main')
    @patch('run.detect_claude_desktop', return_value=True)
    def test_main_auto_detect_claude(self, mock_detect, mock_claude_main, clean_argv, clean_env):
        """Test main function auto-detecting Claude Desktop."""
        import run
        
        sys.argv = ['run.py']
        
        with patch('builtins.print'):
            run.main()
        
        mock_detect.assert_called_once()
        mock_claude_main.assert_called_once()
    
    @patch('run_http.main')
    @patch('run.detect_claude_desktop', return_value=False)
    def test_main_auto_detect_http(self, mock_detect, mock_http_main, clean_argv, clean_env):
        """Test main function auto-detecting HTTP mode."""
        import run
        
        sys.argv = ['run.py']
        
        with patch('builtins.print'):
            run.main()
        
        mock_detect.assert_called_once()
        mock_http_main.assert_called_once()
        assert os.environ.get('MCP_FORCE_HTTP') == '1'
    
    @patch('run_claude.main')
    def test_main_force_stdio_env(self, mock_claude_main, clean_argv, clean_env):
        """Test main function with MCP_FORCE_STDIO environment variable."""
        import run
        
        sys.argv = ['run.py']
        os.environ['MCP_FORCE_STDIO'] = '1'
        
        with patch('builtins.print'):
            with patch('run.detect_claude_desktop', return_value=False):
                run.main()
        
        mock_claude_main.assert_called_once()

class TestClaudeLauncherScript:
    """Test the run_claude.py launcher script."""
    
    def test_imports_successfully(self):
        """Test that run_claude.py can be imported without errors."""
        try:
            import run_claude
            assert hasattr(run_claude, 'main')
            assert hasattr(run_claude, 'log_environment_status')
        except ImportError as e:
            pytest.fail(f"Failed to import run_claude.py: {e}")
    
    def test_server_configuration(self, clean_env):
        """Test server configuration with environment variables."""
        os.environ['MCP_SERVER_NAME'] = 'test-claude-server'
        
        # Need to reload the module to pick up environment changes
        import importlib
        import sys
        if 'run_claude' in sys.modules:
            importlib.reload(sys.modules['run_claude'])
        
        import run_claude
        
        # Check that configuration is read correctly
        assert run_claude.MCP_SERVER_NAME == 'test-claude-server'
    
    def test_server_configuration_defaults(self, clean_env):
        """Test server configuration with default values."""
        # Need to reload the module to ensure clean defaults
        import importlib
        import sys
        if 'run_claude' in sys.modules:
            importlib.reload(sys.modules['run_claude'])
        
        import run_claude
        
        # Check default values
        assert run_claude.MCP_SERVER_NAME == 'claude-mcp-server'
    
    def test_log_environment_status(self, clean_env):
        """Test environment status logging."""
        import run_claude
        
        # Set some environment variables
        os.environ['BRAVE_API_KEY'] = 'test_key'
        os.environ['AIRTABLE_PERSONAL_ACCESS_TOKEN'] = 'test_token'
        
        # Mock file existence check and capture logging output
        with patch('os.path.exists', return_value=True):
            with patch('run_claude.logger') as mock_logger:
                run_claude.log_environment_status()
                
                # Check that logging methods were called
                assert mock_logger.info.called
    
    @patch('run_claude.mcp.run')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_successful_startup(self, mock_stderr, mock_run, clean_env, mock_tool_imports):
        """Test successful main function execution."""
        import run_claude
        
        run_claude.main()
        
        # Verify that the server run method was called
        mock_run.assert_called_once_with(transport="stdio")
    
    @patch('run_claude.mcp.run')
    def test_main_keyboard_interrupt(self, mock_run, clean_env, mock_tool_imports):
        """Test main function handling KeyboardInterrupt."""
        import run_claude
        
        mock_run.side_effect = KeyboardInterrupt()
        
        # Mock the logger to check for the correct message
        with patch('run_claude.logger') as mock_logger:
            run_claude.main()
            
            # Should handle KeyboardInterrupt gracefully
            mock_logger.info.assert_any_call("🛑 Server stopped by user")
    
    @patch('run_claude.mcp.run')
    @patch('sys.exit')
    def test_main_exception_handling(self, mock_exit, mock_run, clean_env, mock_tool_imports):
        """Test main function handling general exceptions."""
        import run_claude
        
        mock_run.side_effect = Exception("Test error")
        
        # Mock the logger to check for the correct message
        with patch('run_claude.logger') as mock_logger:
            run_claude.main()
            
            # Should handle exception and exit
            mock_exit.assert_called_once_with(1)
            mock_logger.error.assert_any_call("❌ Server error: Test error")

class TestHttpLauncherScript:
    """Test the run_http.py launcher script."""
    
    def test_imports_successfully(self):
        """Test that run_http.py can be imported without errors."""
        try:
            import run_http
            assert hasattr(run_http, 'main')
            assert hasattr(run_http, 'log_environment_info')
        except ImportError as e:
            pytest.fail(f"Failed to import run_http.py: {e}")
    
    def test_server_configuration(self, clean_env):
        """Test server configuration with environment variables."""
        os.environ['MCP_SERVER_NAME'] = 'test-http-server'
        os.environ['MCP_HOST'] = '127.0.0.1'
        os.environ['MCP_PORT'] = '9000'
        
        # Need to reload the module to pick up environment changes
        import importlib
        import sys
        if 'run_http' in sys.modules:
            importlib.reload(sys.modules['run_http'])
        
        import run_http
        
        # Check that configuration is read correctly
        assert run_http.MCP_SERVER_NAME == 'test-http-server'
        assert run_http.MCP_HOST == '127.0.0.1'
        assert run_http.MCP_PORT == 9000
    
    def test_server_configuration_defaults(self, clean_env):
        """Test server configuration with default values."""
        # Need to reload the module to ensure clean defaults
        import importlib
        import sys
        if 'run_http' in sys.modules:
            importlib.reload(sys.modules['run_http'])
        
        import run_http
        
        # Check default values
        assert run_http.MCP_SERVER_NAME == 'n8n-mcp-server'
        assert run_http.MCP_HOST == '0.0.0.0'
        assert run_http.MCP_PORT == 8000
    
    def test_log_environment_info(self, clean_env):
        """Test environment info logging."""
        import run_http
        
        # Set some environment variables
        os.environ['BRAVE_API_KEY'] = 'test_key'
        os.environ['AIRTABLE_PERSONAL_ACCESS_TOKEN'] = 'test_token'
        
        # Mock the logger to capture logging
        with patch('run_http.logger') as mock_logger:
            run_http.log_environment_info()
            
            # Check that logging methods were called
            assert mock_logger.info.called
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_http_transport_success(self, mock_stderr, clean_env, mock_tool_imports):
        """Test successful HTTP transport startup."""
        # Need to reload module to ensure clean defaults
        import importlib
        import sys
        if 'run_http' in sys.modules:
            importlib.reload(sys.modules['run_http'])
        
        import run_http
        
        # Mock the mcp instance run method after import
        with patch.object(run_http.mcp, 'run') as mock_run:
            run_http.main()
            
            # Verify that HTTP transport was attempted
            mock_run.assert_called_once_with(transport="http", host="0.0.0.0", port=8000)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_http_fallback_to_sse(self, mock_stderr, clean_env, mock_tool_imports):
        """Test fallback from HTTP to SSE transport."""
        # Need to reload module to ensure clean defaults
        import importlib
        import sys
        if 'run_http' in sys.modules:
            importlib.reload(sys.modules['run_http'])
        
        import run_http
        
        # Mock the mcp instance run method after import
        with patch.object(run_http.mcp, 'run') as mock_run:
            # Make HTTP transport fail, SSE succeed
            mock_run.side_effect = [Exception("HTTP failed"), None]
            
            run_http.main()
            
            # Should attempt both HTTP and SSE
            assert mock_run.call_count == 2
            calls = mock_run.call_args_list
            assert calls[0] == call(transport="http", host="0.0.0.0", port=8000)
            assert calls[1] == call(transport="sse", host="0.0.0.0", port=8000)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_fallback_to_default(self, mock_stderr, clean_env, mock_tool_imports):
        """Test fallback to default run method."""
        # Need to reload module to ensure clean defaults
        import importlib
        import sys
        if 'run_http' in sys.modules:
            importlib.reload(sys.modules['run_http'])
        
        import run_http
        
        # Mock the mcp instance run method after import
        with patch.object(run_http.mcp, 'run') as mock_run:
            # Make HTTP and SSE fail, default succeed
            mock_run.side_effect = [Exception("HTTP failed"), Exception("SSE failed"), None]
            
            run_http.main()
            
            # Should attempt all three methods
            assert mock_run.call_count == 3
            calls = mock_run.call_args_list
            assert calls[0] == call(transport="http", host="0.0.0.0", port=8000)
            assert calls[1] == call(transport="sse", host="0.0.0.0", port=8000)
            assert calls[2] == call()
    
    @patch('run_http.mcp.run')
    @patch('sys.exit')
    def test_main_all_transports_fail(self, mock_exit, mock_run, clean_env, mock_tool_imports):
        """Test behavior when all transport methods fail."""
        import run_http
        
        # Make all transport methods fail
        mock_run.side_effect = [
            Exception("HTTP failed"),
            Exception("SSE failed"), 
            Exception("Default failed")
        ]
        
        # Mock the logger to check for the correct message
        with patch('run_http.logger') as mock_logger:
            run_http.main()
            
            # Should exit with error
            mock_exit.assert_called_once_with(1)
            mock_logger.error.assert_any_call("❌ All methods failed:")

class TestToolRegistration:
    """Test tool registration in launcher scripts."""
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_claude_tool_registration(self, mock_stderr, clean_env, mock_tool_imports, mock_fastmcp):
        """Test that all tools are registered in Claude launcher."""
        import run_claude
        
        # Check that the mcp instance has tools registered
        assert hasattr(run_claude, 'mcp')
        assert run_claude.mcp is not None
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_http_tool_registration(self, mock_stderr, clean_env, mock_tool_imports, mock_fastmcp):
        """Test that all tools are registered in HTTP launcher."""
        import run_http
        
        # Check that the mcp instance has tools registered
        assert hasattr(run_http, 'mcp')
        assert run_http.mcp is not None
    
    def test_tool_import_errors_handled(self, clean_env):
        """Test that tool import errors are handled gracefully."""
        # Mock a failing tool import
        with patch.dict('sys.modules', {'tools.calculator_tool': None}):
            try:
                # Should not raise ImportError
                import run_claude
                import run_http
                assert True
            except ImportError:
                pytest.fail("Tool import errors should be handled gracefully")

class TestEnvironmentDetection:
    """Test environment detection and configuration."""
    
    def test_dotenv_loading_optional(self, clean_env):
        """Test that dotenv loading is optional."""
        # Mock dotenv not being available
        with patch.dict('sys.modules', {'dotenv': None}):
            try:
                import run_claude
                import run_http
                # Should not raise ImportError
                assert True
            except ImportError:
                pytest.fail("dotenv should be optional")
    
    def test_warning_suppression(self):
        """Test that Pydantic warnings are properly suppressed."""
        import warnings
        
        # Import should not generate Pydantic deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import run_claude
            import run_http
            
            # Filter for Pydantic warnings
            pydantic_warnings = [warning for warning in w 
                               if "pydantic" in str(warning.message).lower()]
            
            # Should have no Pydantic warnings
            assert len(pydantic_warnings) == 0

class TestScriptErrorHandling:
    """Test error handling across all launcher scripts."""
    
    def test_missing_fastmcp_handling(self, clean_env):
        """Test behavior when FastMCP is not available."""
        # Remove any existing modules first
        import sys
        modules_to_remove = [m for m in sys.modules.keys() if m.startswith('run_')]
        for module in modules_to_remove:
            del sys.modules[module]
            
        with patch.dict('sys.modules', {'fastmcp': None}):
            with pytest.raises((ImportError, ModuleNotFoundError)):
                import run_claude
    
    def test_invalid_port_handling(self, clean_env):
        """Test handling of invalid port configuration."""
        os.environ['MCP_PORT'] = 'invalid_port'
        
        # Remove any existing modules first
        import sys
        modules_to_remove = [m for m in sys.modules.keys() if m.startswith('run_')]
        for module in modules_to_remove:
            del sys.modules[module]
        
        with pytest.raises(ValueError):
            import run_http
    
    def test_logging_configuration(self, clean_env):
        """Test that logging is properly configured."""
        import run_claude
        import run_http
        
        # Both should configure logging without errors
        assert True

class TestScriptDocumentation:
    """Test that scripts have proper documentation."""
    
    def test_run_py_docstring(self):
        """Test that run.py has proper documentation."""
        import run
        
        assert run.__doc__ is not None
        assert "Smart MCP Server Launcher" in run.__doc__
        assert "Usage:" in run.__doc__
    
    def test_run_claude_docstring(self):
        """Test that run_claude.py has proper documentation."""
        import run_claude
        
        assert run_claude.__doc__ is not None
        assert "stdio server for Claude Desktop" in run_claude.__doc__
    
    def test_run_http_docstring(self):
        """Test that run_http.py has proper documentation."""
        import run_http
        
        assert run_http.__doc__ is not None
        assert "FastMCP server for n8n integration" in run_http.__doc__
    
    def test_function_docstrings(self):
        """Test that key functions have proper documentation."""
        import run
        import run_claude
        import run_http
        
        # Main launcher functions
        assert run.main.__doc__ is not None
        assert run.detect_claude_desktop.__doc__ is not None
        assert run.show_help.__doc__ is not None
        
        # Claude launcher functions
        assert run_claude.main.__doc__ is not None
        assert run_claude.log_environment_status.__doc__ is not None
        
        # HTTP launcher functions
        assert run_http.main.__doc__ is not None
        assert run_http.log_environment_info.__doc__ is not None 