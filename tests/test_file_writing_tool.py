import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
from tools.file_writing_tool import (
    write_file, create_directory, write_multiple_files, 
    get_playground_info, create_project_structure, register
)


class TestFileWritingTool:
    """Test suite for the file writing tool."""
    
    @pytest.mark.asyncio
    async def test_write_file_success(self, temp_playground_dir, assert_success_response):
        """Test successful file writing."""
        result = await write_file("test.txt", "Hello, world!")
        
        assert_success_response(result)
        assert result["file_path"]
        assert result["content_length"] == 13
        
        # Verify file was actually created
        written_file = Path(temp_playground_dir) / "test.txt"
        assert written_file.exists()
        assert written_file.read_text() == "Hello, world!"
    
    @pytest.mark.asyncio
    async def test_write_file_nested_directory(self, temp_playground_dir, assert_success_response):
        """Test writing file in nested directory structure."""
        result = await write_file("subdir/nested/test.txt", "Nested content")
        
        assert_success_response(result)
        
        # Verify nested directories were created
        nested_file = Path(temp_playground_dir) / "subdir" / "nested" / "test.txt"
        assert nested_file.exists()
        assert nested_file.read_text() == "Nested content"
    
    @pytest.mark.asyncio
    async def test_write_file_overwrite(self, temp_playground_dir, assert_success_response):
        """Test overwriting existing files."""
        # Create initial file
        await write_file("test.txt", "Original content")
        
        # Overwrite with new content
        result = await write_file("test.txt", "New content", overwrite=True)
        
        assert_success_response(result)
        
        # Verify content was overwritten
        test_file = Path(temp_playground_dir) / "test.txt"
        assert test_file.read_text() == "New content"
    
    @pytest.mark.asyncio
    async def test_write_file_no_overwrite(self, temp_playground_dir, assert_error_response):
        """Test protection against overwriting when disabled."""
        # Create initial file
        await write_file("test.txt", "Original content")
        
        # Try to overwrite with overwrite disabled
        result = await write_file("test.txt", "New content", overwrite=False)
        
        assert_error_response(result, "already exists")
        
        # Verify original content preserved
        test_file = Path(temp_playground_dir) / "test.txt"
        assert test_file.read_text() == "Original content"
    
    @pytest.mark.asyncio
    async def test_write_file_different_encodings(self, temp_playground_dir, assert_success_response):
        """Test writing files with different encodings."""
        content = "Hello, Wörld! 你好"
        
        result = await write_file("utf8.txt", content, encoding="utf-8")
        assert_success_response(result)
        
        # Verify file can be read back correctly
        test_file = Path(temp_playground_dir) / "utf8.txt"
        assert test_file.read_text(encoding="utf-8") == content
    
    @pytest.mark.asyncio
    async def test_create_directory_success(self, temp_playground_dir, assert_success_response):
        """Test successful directory creation."""
        result = await create_directory("new_directory")
        
        assert_success_response(result)
        assert result["directory_path"]
        
        # Verify directory was created
        new_dir = Path(temp_playground_dir) / "new_directory"
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    @pytest.mark.asyncio
    async def test_create_nested_directories(self, temp_playground_dir, assert_success_response):
        """Test creating nested directory structures."""
        result = await create_directory("level1/level2/level3")
        
        assert_success_response(result)
        
        # Verify all levels were created
        level3_dir = Path(temp_playground_dir) / "level1" / "level2" / "level3"
        assert level3_dir.exists()
        assert level3_dir.is_dir()
    
    @pytest.mark.asyncio
    async def test_write_multiple_files_success(self, temp_playground_dir, assert_success_response):
        """Test writing multiple files in batch."""
        files_data = [
            {"path": "file1.txt", "content": "Content 1"},
            {"path": "subdir/file2.txt", "content": "Content 2"},
            {"path": "file3.json", "content": '{"key": "value"}'}
        ]
        
        result = await write_multiple_files(files_data)
        
        assert_success_response(result)
        assert "results" in result
        assert len(result["results"]) == 3
        
        # Verify all files were created
        for file_data in files_data:
            file_path = Path(temp_playground_dir) / file_data["path"]
            assert file_path.exists()
            assert file_path.read_text() == file_data["content"]
    
    @pytest.mark.asyncio
    async def test_write_multiple_files_partial_failure(self, temp_playground_dir):
        """Test handling partial failures in batch write operations."""
        files_data = [
            {"path": "valid_file.txt", "content": "Valid content"},
            {"path": "/invalid/absolute/path.txt", "content": "Should fail"},
            {"path": "another_valid.txt", "content": "Another valid"}
        ]
        
        result = await write_multiple_files(files_data)
        
        # Should report both successes and failures
        assert "results" in result
        # Check that we have failed writes
        assert result["failed_writes"] > 0  # Should have at least one failed write
    
    @pytest.mark.asyncio
    async def test_get_playground_info(self, temp_playground_dir, assert_success_response):
        """Test getting playground directory information."""
        result = await get_playground_info()
        
        assert_success_response(result)
        assert "playground_root" in result
        assert "exists" in result
        assert result["exists"] is True
        assert temp_playground_dir in result["playground_root"]
    
    @pytest.mark.asyncio
    async def test_create_project_structure_web(self, temp_playground_dir, assert_success_response):
        """Test creating web project structure."""
        result = await create_project_structure("my_web_project", "web")
        
        assert_success_response(result)
        assert "project_root" in result
        assert "files_created" in result
        
        # Verify typical web project files were created
        project_dir = Path(temp_playground_dir) / "my_web_project"
        assert project_dir.exists()
        assert (project_dir / "index.html").exists()
        assert (project_dir / "css" / "style.css").exists()
        assert (project_dir / "js" / "script.js").exists()
    
    @pytest.mark.asyncio
    async def test_create_project_structure_python(self, temp_playground_dir, assert_success_response):
        """Test creating Python project structure."""
        result = await create_project_structure("my_python_project", "python")
        
        assert_success_response(result)
        
        # Verify typical Python project files were created
        project_dir = Path(temp_playground_dir) / "my_python_project"
        assert project_dir.exists()
        assert (project_dir / "main.py").exists()
        assert (project_dir / "requirements.txt").exists()
        assert (project_dir / "README.md").exists()
    

    
    @pytest.mark.asyncio
    async def test_create_project_structure_with_custom_files(self, temp_playground_dir, assert_success_response):
        """Test creating project structure with additional custom files."""
        custom_files = {
            "config.yaml": "database:\n  host: localhost\n  port: 5432",
            "docs/api.md": "# API Documentation\nThis is the API documentation."
        }
        
        result = await create_project_structure(
            "custom_project", 
            "general", 
            files=custom_files
        )
        
        assert_success_response(result)
        
        # Verify custom files were created
        project_dir = Path(temp_playground_dir) / "custom_project"
        assert (project_dir / "config.yaml").exists()
        assert (project_dir / "docs" / "api.md").exists()
        
        # Verify content
        assert "database:" in (project_dir / "config.yaml").read_text()
        assert "API Documentation" in (project_dir / "docs" / "api.md").read_text()
    
    @pytest.mark.asyncio
    async def test_sandbox_security_absolute_path(self, assert_error_response):
        """Test that absolute paths outside playground are rejected."""
        result = await write_file("/etc/passwd", "malicious content")
        assert_error_response(result, "Path must be within the playground directory")
    
    @pytest.mark.asyncio
    async def test_sandbox_security_directory_traversal(self, assert_error_response):
        """Test that directory traversal attempts are blocked."""
        result = await write_file("../../../etc/passwd", "malicious content")
        assert_error_response(result, "Path must be within the playground directory")
    
    @pytest.mark.asyncio
    async def test_sandbox_security_symlink_attack(self, temp_playground_dir, assert_error_response):
        """Test protection against symlink attacks."""
        # This test may vary based on implementation
        result = await write_file("../sensitive_file.txt", "should not work")
        assert_error_response(result, "Path must be within the playground directory")
    
    @pytest.mark.asyncio
    async def test_file_size_handling(self, temp_playground_dir, assert_success_response):
        """Test handling of different file sizes."""
        # Small file
        result = await write_file("small.txt", "small content")
        assert_success_response(result)
        
        # Larger file
        large_content = "x" * 10000  # 10KB
        result = await write_file("large.txt", large_content)
        assert_success_response(result)
        
        # Verify content integrity
        large_file = Path(temp_playground_dir) / "large.txt"
        assert len(large_file.read_text()) == 10000
    
    @pytest.mark.asyncio
    async def test_special_characters_in_paths(self, temp_playground_dir):
        """Test handling of special characters in file paths."""
        # Test various special characters that might be problematic
        test_cases = [
            ("file with spaces.txt", "content"),
            ("file-with-dashes.txt", "content"),
            ("file_with_underscores.txt", "content"),
            ("file.with.dots.txt", "content"),
        ]
        
        for filename, content in test_cases:
            result = await write_file(filename, content)
            assert result["status"] == "success"
            
            # Verify file exists
            test_file = Path(temp_playground_dir) / filename
            assert test_file.exists()
    
    @pytest.mark.asyncio
    async def test_empty_content_handling(self, temp_playground_dir, assert_success_response):
        """Test writing files with empty content."""
        result = await write_file("empty.txt", "")
        
        assert_success_response(result)
        
        # Verify empty file was created
        empty_file = Path(temp_playground_dir) / "empty.txt"
        assert empty_file.exists()
        assert empty_file.read_text() == ""
        assert empty_file.stat().st_size == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_file_operations(self, temp_playground_dir):
        """Test concurrent file writing operations."""
        import asyncio
        
        # Create multiple write operations concurrently
        tasks = [
            write_file(f"concurrent_{i}.txt", f"Content {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        for result in results:
            assert result["status"] == "success"
        
        # Verify all files were created
        for i in range(5):
            test_file = Path(temp_playground_dir) / f"concurrent_{i}.txt"
            assert test_file.exists()
            assert test_file.read_text() == f"Content {i}"
    
    def test_registration(self, fastmcp_server):
        """Test that file writing tools register correctly."""
        # Call the register function
        register(fastmcp_server)
        
        # Check that expected file writing tools are registered
        expected_tools = [
            "write_file", "create_directory", "write_multiple_files",
            "get_playground_info", "create_project_structure"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in fastmcp_server._registered_functions
            assert tool_name in fastmcp_server._tool_manager._tools
            
        # Verify tool method was called for each function
        assert fastmcp_server.tool.call_count == len(expected_tools)
    

    
    @pytest.mark.asyncio
    async def test_error_handling_permission_denied(self, assert_error_response):
        """Test error handling for permission denied."""
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            result = await write_file("restricted/test.txt", "content")
            assert_error_response(result, "Permission denied")
    
    @pytest.mark.asyncio
    async def test_response_format_consistency(self, temp_playground_dir):
        """Test that all functions return consistent response formats."""
        # Test write_file response format
        result = await write_file("test.txt", "content")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ["success", "error"]
        
        if result["status"] == "success":
            assert "file_path" in result
            assert "content_length" in result
        else:
            assert "error" in result 