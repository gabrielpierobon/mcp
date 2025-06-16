import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import httpx
import os
from tools.brave_search import brave_web_search, brave_local_search, register


class TestBraveSearchTool:
    """Test suite for the Brave Search tool."""
    
    @pytest.mark.asyncio
    async def test_web_search_success(self, mock_env_vars, mock_brave_search_response, assert_success_response):
        """Test successful web search."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_brave_search_response
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_web_search("test query")
            
            assert_success_response(result)
            assert result["query"] == "test query"
            assert len(result["results"]) == 2
            assert result["total_count"] == 2
            assert result["results"][0]["title"] == "Test Result 1"
    
    @pytest.mark.asyncio
    async def test_web_search_with_pagination(self, mock_env_vars, mock_brave_search_response, assert_success_response):
        """Test web search with count and offset parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_brave_search_response
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_web_search("test query", count=5, offset=2)
            
            assert_success_response(result)
            assert result["query"] == "test query"
            
            # Verify the API was called with correct parameters
            call_args = mock_context.get.call_args
            assert call_args[1]["params"]["count"] == 5
            assert call_args[1]["params"]["offset"] == 2
    
    @pytest.mark.asyncio
    async def test_web_search_no_api_key(self, assert_error_response):
        """Test web search without API key."""
        with patch('tools.brave_search.BRAVE_API_KEY', None):
            result = await brave_web_search("test query")
            assert_error_response(result, "BRAVE_API_KEY is not configured")
    
    @pytest.mark.asyncio
    async def test_web_search_invalid_count(self, mock_env_vars, assert_error_response):
        """Test web search with invalid count parameter."""
        result = await brave_web_search("test query", count=25)
        assert_error_response(result, "Count must be between 1 and 20")
        
        result = await brave_web_search("test query", count=0)
        assert_error_response(result, "Count must be between 1 and 20")
    
    @pytest.mark.asyncio
    async def test_web_search_invalid_offset(self, mock_env_vars, assert_error_response):
        """Test web search with invalid offset parameter."""
        result = await brave_web_search("test query", offset=10)
        assert_error_response(result, "Offset must be between 0 and 9")
        
        result = await brave_web_search("test query", offset=-1)
        assert_error_response(result, "Offset must be between 0 and 9")
    
    @pytest.mark.asyncio
    async def test_web_search_api_error(self, mock_env_vars, assert_error_response):
        """Test web search API error response."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden: Invalid API key"
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_web_search("test query")
            assert_error_response(result, "status code 403")
    
    @pytest.mark.asyncio
    async def test_web_search_network_error(self, mock_env_vars, assert_error_response):
        """Test web search network error handling."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.side_effect = httpx.NetworkError("Connection failed")
            
            result = await brave_web_search("test query")
            assert_error_response(result, "Tool execution failed")
    
    @pytest.mark.asyncio
    async def test_local_search_success(self, mock_env_vars, assert_success_response):
        """Test successful local search."""
        mock_local_response = {
            "local": {
                "places": [
                    {
                        "name": "Test Business",
                        "address": "123 Test St",
                        "rating": 4.5
                    }
                ]
            }
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_local_response
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_local_search("restaurants near me")
            
            assert_success_response(result)
            assert result["query"] == "restaurants near me"
            assert len(result["places"]) == 1
            assert result["places"][0]["name"] == "Test Business"
    
    @pytest.mark.asyncio
    async def test_local_search_fallback_to_web(self, mock_env_vars, mock_brave_search_response, assert_success_response):
        """Test local search fallback to web search when no local results."""
        # First call (local search) returns empty results
        mock_local_response = {"local": {"places": []}}
        mock_response_local = Mock()
        mock_response_local.status_code = 200
        mock_response_local.json.return_value = mock_local_response
        
        # Second call (web search fallback) returns web results
        mock_response_web = Mock()
        mock_response_web.status_code = 200
        mock_response_web.json.return_value = mock_brave_search_response
        
        # Mock httpx.AsyncClient properly with side_effect for multiple calls
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.side_effect = [mock_response_local, mock_response_web]
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_local_search("test query")
            
            assert_success_response(result)
            assert "results" in result  # Should have web search results
            assert len(result["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_local_search_invalid_count(self, mock_env_vars, assert_error_response):
        """Test local search with invalid count parameter."""
        result = await brave_local_search("test query", count=25)
        assert_error_response(result, "Count must be between 1 and 20")
    
    @pytest.mark.asyncio
    async def test_local_search_no_api_key(self, assert_error_response):
        """Test local search without API key."""
        with patch('tools.brave_search.BRAVE_API_KEY', None):
            result = await brave_local_search("test query")
            assert_error_response(result, "BRAVE_API_KEY is not configured")
    
    def test_registration(self, fastmcp_server):
        """Test that both search tools register correctly."""
        # Call the register function
        register(fastmcp_server)
        
        # Verify both functions were registered
        assert 'brave_web_search' in fastmcp_server._registered_functions
        assert 'brave_local_search' in fastmcp_server._registered_functions
        
        # Verify they were added to the tool manager
        tool_manager = fastmcp_server._tool_manager
        assert 'brave_web_search' in tool_manager._tools
        assert 'brave_local_search' in tool_manager._tools
        
        # Verify tool method was called twice (once for each function)
        assert fastmcp_server.tool.call_count == 2
    
    @pytest.mark.asyncio
    async def test_web_search_response_format(self, mock_env_vars, mock_brave_search_response):
        """Test that web search response follows expected format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_brave_search_response
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_web_search("test")
            
            # Check required fields
            assert "query" in result
            assert "results" in result
            assert "total_count" in result
            assert "status" in result
            assert result["status"] == "success"
            
            # Check optional metrics
            assert "news_count" in result
            assert "videos_count" in result
            assert "web_count" in result
    
    @pytest.mark.asyncio
    async def test_local_search_response_format(self, mock_env_vars):
        """Test that local search response follows expected format."""
        mock_local_response = {
            "local": {
                "places": [{"name": "Test Place"}]
            }
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_local_response
        
        # Mock httpx.AsyncClient properly
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_context.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_context
            
            result = await brave_local_search("test")
            
            # Check required fields
            assert "query" in result
            assert "places" in result
            assert "total_count" in result
            assert "status" in result
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_api_headers_and_params(self, mock_env_vars, mock_brave_search_response):
        """Test that correct headers and parameters are sent to API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_brave_search_response
        
        # Patch the BRAVE_API_KEY directly since it's loaded at import time
        with patch('tools.brave_search.BRAVE_API_KEY', 'test_brave_key'):
            # Mock httpx.AsyncClient properly
            with patch('httpx.AsyncClient') as mock_client:
                mock_context = AsyncMock()
                mock_context.get.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_context
                
                await brave_web_search("test query", count=15, offset=5)
                
                # Check the API call
                call_args = mock_context.get.call_args
                
                # Check URL
                assert "api.search.brave.com" in call_args[0][0]
                
                # Check parameters
                params = call_args[1]["params"]
                assert params["q"] == "test query"
                assert params["count"] == 15
                assert params["offset"] == 5
                
                # Check headers
                headers = call_args[1]["headers"]
                assert headers["Accept"] == "application/json"
                assert headers["Accept-Encoding"] == "gzip"
                assert headers["X-Subscription-Token"] == "test_brave_key" 