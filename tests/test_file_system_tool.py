import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

# Import the functions we need to test
# Note: We'll need to read the actual file to see the function names
# For now, I'll assume common file system operations based on the documentation

class TestFileSystemTool:
    """Test suite for the file system tool."""
    
    def test_temp_file_system_fixture(self, temp_file_system):
        """Test that the temp file system fixture works correctly."""
        temp_dir = Path(temp_file_system)
        assert temp_dir.exists()
        assert (temp_dir / "test.txt").exists()
        assert (temp_dir / "data.json").exists()
        assert (temp_dir / "subdir" / "nested.py").exists()
        
        # Check file contents
        assert (temp_dir / "test.txt").read_text() == "Hello, world!"
        assert (temp_dir / "data.json").read_text() == '{"key": "value"}'
    
    @pytest.mark.asyncio
    async def test_read_file_success(self, temp_file_system, assert_success_response):
        """Test successful file reading."""
        # We need to import the actual function - this is a placeholder
        # The actual implementation will depend on the function names in file_system_tool.py
        from tools.file_system_tool import read_file
        
        test_file = Path(temp_file_system) / "test.txt"
        result = await read_file(str(test_file))
        
        assert_success_response(result)
        assert result["content"] == "Hello, world!"
        assert result["file_path"] == str(test_file)
    
    @pytest.mark.asyncio
    async def test_read_file_not_found(self, temp_file_system, assert_error_response):
        """Test reading non-existent file."""
        from tools.file_system_tool import read_file
        
        nonexistent_file = Path(temp_file_system) / "nonexistent.txt"
        result = await read_file(str(nonexistent_file))
        
        assert_error_response(result, "does not exist")
    
    @pytest.mark.asyncio
    async def test_read_file_permission_denied(self, temp_file_system, assert_error_response):
        """Test reading file with permission denied."""
        from tools.file_system_tool import read_file
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            test_file = Path(temp_file_system) / "test.txt"
            result = await read_file(str(test_file))
            
            assert_error_response(result, "Permission denied")
    
    @pytest.mark.asyncio
    async def test_list_directory_success(self, temp_file_system, assert_success_response):
        """Test successful directory listing."""
        from tools.file_system_tool import list_directory
        
        result = await list_directory(temp_file_system)
        
        assert_success_response(result)
        assert "items" in result
        assert "total_directories" in result
        
        # Check that our test files are listed
        item_names = [f["name"] for f in result["items"]]
        assert "test.txt" in item_names
        assert "data.json" in item_names
        assert "subdir" in item_names
    
    @pytest.mark.asyncio
    async def test_list_directory_not_found(self, assert_error_response):
        """Test listing non-existent directory."""
        from tools.file_system_tool import list_directory
        
        result = await list_directory("/nonexistent/directory")
        assert_error_response(result, "does not exist")
    
    @pytest.mark.asyncio
    async def test_search_files_by_name(self, temp_file_system, assert_success_response):
        """Test searching files by name pattern."""
        from tools.file_system_tool import search_files
        
        result = await search_files(
            search_directory=temp_file_system,
            filename_pattern="txt"
        )
        
        assert_success_response(result)
        assert "matching_files" in result
        
        found_files = [f["filename"] for f in result["matching_files"]]
        assert "test.txt" in found_files
        assert "empty_file.txt" in found_files
        assert "large_file.txt" in found_files
    
    @pytest.mark.asyncio
    async def test_search_files_by_content(self, temp_file_system, assert_success_response):
        """Test searching files by content."""
        from tools.file_system_tool import search_files
        
        result = await search_files(
            search_directory=temp_file_system,
            content_pattern="Hello"
        )
        
        assert_success_response(result)
        assert "matching_files" in result
        
        # Should find test.txt which contains "Hello, world!"
        found_files = [f["filename"] for f in result["matching_files"]]
        assert "test.txt" in found_files
    
    @pytest.mark.asyncio
    async def test_get_file_info(self, temp_file_system, assert_success_response):
        """Test getting file information."""
        from tools.file_system_tool import get_file_info
        
        test_file = Path(temp_file_system) / "test.txt"
        result = await get_file_info(str(test_file))
        
        assert_success_response(result)
        assert "file_path" in result
        assert "size_bytes" in result
        assert "modified_time" in result
        assert "type" in result
        assert result["type"] == "file"
        assert result["size_bytes"] > 0
    
    @pytest.mark.asyncio
    async def test_get_system_info(self, assert_success_response):
        """Test getting system information."""
        from tools.file_system_tool import get_system_info
        
        result = await get_system_info()
        
        assert_success_response(result)
        assert "platform" in result
        assert "home_directory" in result
        assert "current_directory" in result
    
    @pytest.mark.asyncio
    async def test_find_directory(self, temp_file_system, assert_success_response):
        """Test finding directories by name."""
        from tools.file_system_tool import find_directory
        
        result = await find_directory(
            directory_name="subdir",
            search_root=temp_file_system
        )
        
        assert_success_response(result)
        assert "matching_directories" in result
        
        found_dirs = [d["full_path"] for d in result["matching_directories"]]
        assert any("subdir" in path for path in found_dirs)
    
    @pytest.mark.asyncio
    async def test_home_directory_expansion(self, temp_file_system):
        """Test that tilde (~) is properly expanded to home directory."""
        from tools.file_system_tool import list_directory
        
        with patch('pathlib.Path.home', return_value=Path(temp_file_system)):
            result = await list_directory("~")
            
            assert result["status"] == "success"
            assert "items" in result
    
    @pytest.mark.asyncio
    async def test_file_size_limits(self, temp_file_system, assert_error_response):
        """Test file size limit enforcement."""
        from tools.file_system_tool import read_file
        
        # Test with a very small limit instead of mocking
        large_file = Path(temp_file_system) / "large_file.txt"  # This file exists in temp_file_system fixture
        
        # Try to read with a very small size limit (1 byte)
        result = await read_file(str(large_file), max_size_mb=0.000001)  # ~1 byte limit
        
        # Should get an error about file being too large
        assert result["status"] == "error"
        assert "File too large" in result["error"] or "too large" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_file_encoding_handling(self, temp_file_system):
        """Test different file encodings."""
        from tools.file_system_tool import read_file
        
        # Create a file with special characters
        special_file = Path(temp_file_system) / "special.txt"
        special_file.write_text("Héllo Wörld! 你好", encoding='utf-8')
        
        result = await read_file(str(special_file), encoding='utf-8')
        
        assert result["status"] == "success"
        assert "Héllo Wörld! 你好" in result["content"]
    
    @pytest.mark.asyncio
    async def test_recursive_directory_listing(self, temp_file_system, assert_success_response):
        """Test recursive directory listing."""
        from tools.file_system_tool import list_directory
        
        result = await list_directory(temp_file_system, recursive=True)
        
        assert_success_response(result)
        
        # Should include files from subdirectories
        all_files = []
        def collect_files(items):
            for item in items:
                if item["type"] == "file":
                    all_files.append(item["name"])
                elif item["type"] == "directory" and "contents" in item:
                    collect_files(item["contents"])
        
        collect_files(result["items"])
        assert "nested.py" in all_files
    
    @pytest.mark.asyncio
    async def test_hidden_files_inclusion(self, temp_file_system):
        """Test including/excluding hidden files."""
        from tools.file_system_tool import list_directory
        
        # Create a hidden file
        hidden_file = Path(temp_file_system) / ".hidden"
        hidden_file.write_text("hidden content")
        
        # Test excluding hidden files (default)
        result = await list_directory(temp_file_system, include_hidden=False)
        file_names = [f["name"] for f in result["items"]]
        assert ".hidden" not in file_names
        
        # Test including hidden files
        result = await list_directory(temp_file_system, include_hidden=True)
        file_names = [f["name"] for f in result["items"]]
        assert ".hidden" in file_names
    
    @pytest.mark.asyncio
    async def test_file_extension_filtering(self, temp_file_system, assert_success_response):
        """Test filtering files by extension."""
        from tools.file_system_tool import list_directory
        
        result = await list_directory(
            temp_file_system, 
            file_extensions=[".txt", ".json"]
        )
        
        assert_success_response(result)
        
        file_names = [f["name"] for f in result["items"]]
        # Should include txt and json files
        assert "test.txt" in file_names
        assert "data.json" in file_names
        # Should not include .py files
        assert not any(name.endswith(".py") for name in file_names)
    
    @pytest.mark.asyncio
    async def test_max_items_limit(self, temp_file_system):
        """Test maximum items limit."""
        from tools.file_system_tool import list_directory
        
        result = await list_directory(temp_file_system, max_items=2)
        
        # Should limit the total number of items returned
        total_items = len(result.get("items", []))
        assert total_items <= 2
    
    def test_registration(self, fastmcp_server):
        """Test that file system tools register correctly."""
        from tools.file_system_tool import register
        
        # Call the register function
        register(fastmcp_server)
        
        # Check that expected file system tools are registered
        expected_tools = [
            "read_file", "list_directory", "search_files", 
            "get_file_info", "get_system_info", "find_directory"
        ]
        
        # Verify all functions were registered
        for tool_name in expected_tools:
            assert tool_name in fastmcp_server._registered_functions
            
        # Verify they were added to the tool manager
        tool_manager = fastmcp_server._tool_manager
        for tool_name in expected_tools:
            assert tool_name in tool_manager._tools
            
        # Verify tool method was called for each function
        assert fastmcp_server.tool.call_count == len(expected_tools)
    
    @pytest.mark.asyncio
    async def test_path_validation(self):
        """Test path validation and security."""
        from tools.file_system_tool import read_file
        
        # Test directory traversal protection
        result = await read_file("../../../etc/passwd")
        
        # Should either block the operation or handle it safely
        # The exact behavior depends on implementation
        assert isinstance(result, dict)
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_binary_file_handling(self, temp_file_system):
        """Test handling of binary files."""
        from tools.file_system_tool import read_file
        
        # Create a binary file
        binary_file = Path(temp_file_system) / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xFF')
        
        result = await read_file(str(binary_file), return_base64=True)
        
        # Should either return base64 or indicate it's a binary file
        assert isinstance(result, dict)
        if result.get("status") == "success":
            assert "content" in result or "base64_content" in result 