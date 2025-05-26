# tools/file_system_tool.py
from typing import Dict, Any, Optional, List
import os
import json
import base64
import platform
from pathlib import Path
from datetime import datetime

def _expand_path(path_str: str) -> Path:
    """Helper function to expand path with ~ and environment variables."""
    # Expand ~ to home directory
    if path_str.startswith('~'):
        path_str = str(Path.home()) + path_str[1:]
    
    # Expand environment variables
    path_str = os.path.expandvars(path_str)
    
    return Path(path_str).resolve()

async def get_system_info() -> Dict[str, Any]:
    """
    Get information about the current system and user directories.
    
    Returns:
        Dictionary containing system information and common directory paths
    """
    print("INFO: get_system_info called")
    
    try:
        # Get user home directory
        home_dir = Path.home()
        
        # Get current working directory
        current_dir = Path.cwd()
        
        # Common directories based on OS
        common_dirs = {}
        
        if platform.system() == "Windows":
            common_dirs = {
                "desktop": home_dir / "Desktop",
                "documents": home_dir / "Documents", 
                "downloads": home_dir / "Downloads",
                "pictures": home_dir / "Pictures",
                "music": home_dir / "Music",
                "videos": home_dir / "Videos"
            }
        else:  # Linux/macOS
            common_dirs = {
                "desktop": home_dir / "Desktop",
                "documents": home_dir / "Documents",
                "downloads": home_dir / "Downloads", 
                "pictures": home_dir / "Pictures",
                "music": home_dir / "Music",
                "videos": home_dir / "Videos"
            }
        
        # Check which directories actually exist
        existing_dirs = {}
        for name, path in common_dirs.items():
            if path.exists():
                existing_dirs[name] = str(path)
        
        return {
            "system": platform.system(),
            "platform": platform.platform(),
            "home_directory": str(home_dir),
            "current_directory": str(current_dir),
            "username": os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', os.environ.get('USERNAME', 'unknown')),
            "common_directories": existing_dirs,
            "path_separator": os.sep,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: get_system_info failed: {str(e)}")
        return {
            "error": f"Failed to get system info: {str(e)}",
            "status": "error"
        }

async def read_file(
    file_path: str,
    encoding: str = "utf-8",
    return_base64: bool = False,
    max_size_mb: int = 50
) -> Dict[str, Any]:
    """
    Read content from a file on the local file system.
    
    Args:
        file_path: Path to the file to read (supports ~ for home directory) (required)
        encoding: Text encoding to use (default: "utf-8")
        return_base64: Return content as base64 for binary files (default: False)
        max_size_mb: Maximum file size to read in MB (default: 50)
    
    Returns:
        Dictionary containing file content and metadata
    """
    print(f"INFO: read_file called with path: {file_path}")
    
    try:
        file_path = _expand_path(file_path)
        
        # Security check - ensure file exists and is readable
        if not file_path.exists():
            return {
                "error": f"File does not exist: {file_path}",
                "status": "error"
            }
        
        if not file_path.is_file():
            return {
                "error": f"Path is not a file: {file_path}",
                "status": "error"
            }
        
        # Get file stats
        stat = file_path.stat()
        
        # Check file size limit
        max_size_bytes = max_size_mb * 1024 * 1024
        if stat.st_size > max_size_bytes:
            return {
                "error": f"File too large: {stat.st_size} bytes (max: {max_size_bytes} bytes)",
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "max_size_mb": max_size_mb,
                "status": "error"
            }
        
        if return_base64:
            # Read as binary and encode as base64
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('ascii')
            content_type = "base64"
        else:
            # Read as text
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            content_type = "text"
        
        return {
            "file_path": str(file_path),
            "content": content,
            "content_type": content_type,
            "encoding": encoding if not return_base64 else "base64",
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 3),
            "modified_time": stat.st_mtime,
            "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        }
        
    except UnicodeDecodeError:
        return {
            "error": f"Unable to decode file with encoding '{encoding}'. Try setting return_base64=True for binary files.",
            "status": "error"
        }
    except PermissionError:
        return {
            "error": f"Permission denied accessing file: {file_path}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: read_file failed: {str(e)}")
        return {
            "error": f"Failed to read file: {str(e)}",
            "status": "error"
        }

async def list_directory(
    directory_path: str,
    include_hidden: bool = False,
    recursive: bool = False,
    max_depth: int = 1,  # CHANGED: Default to 1 instead of 3
    file_extensions: Optional[List[str]] = None,
    max_items: int = 50  # NEW: Limit total items returned
) -> Dict[str, Any]:
    """
    List contents of a directory with filtering options and token-efficient controls.
    
    Args:
        directory_path: Path to the directory to list (supports ~ for home directory) (required)
        include_hidden: Include hidden files/directories (default: False)
        recursive: List subdirectories recursively (default: False)
        max_depth: Maximum recursion depth (default: 1, max: 2 for token efficiency)
        file_extensions: Filter by file extensions, e.g., [".txt", ".py"] (optional)
        max_items: Maximum total items to return across all levels (default: 50, max: 100)
    
    Returns:
        Dictionary containing directory listing
    """
    print(f"INFO: list_directory called with path: {directory_path}")
    
    # Enforce strict limits for token efficiency
    max_depth = min(max_depth, 2)  # Hard limit on depth
    max_items = min(max_items, 100)  # Hard limit on items
    
    try:
        directory_path = _expand_path(directory_path)
        
        if not directory_path.exists():
            return {
                "error": f"Directory does not exist: {directory_path}",
                "status": "error"
            }
        
        if not directory_path.is_dir():
            return {
                "error": f"Path is not a directory: {directory_path}",
                "status": "error"
            }
        
        total_items_collected = 0
        truncated = False
        
        def scan_directory(path: Path, current_depth: int = 0):
            nonlocal total_items_collected, truncated
            items = []
            
            if total_items_collected >= max_items:
                truncated = True
                return {"items": [], "directory_count": 0, "file_count": 0}
            
            try:
                for item in path.iterdir():
                    if total_items_collected >= max_items:
                        truncated = True
                        break
                    
                    # Skip hidden files unless requested
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    # Filter by file extensions if specified
                    if file_extensions and item.is_file():
                        if not any(item.name.lower().endswith(ext.lower()) for ext in file_extensions):
                            continue
                    
                    stat = item.stat()
                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "relative_path": str(item.relative_to(directory_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size_bytes": stat.st_size if item.is_file() else None,
                        "size_mb": round(stat.st_size / (1024 * 1024), 3) if item.is_file() else None,
                        "modified_time": stat.st_mtime,
                        "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add file extension for files
                    if item.is_file():
                        item_info["extension"] = item.suffix.lower()
                    
                    # Recursive scanning (with strict limits)
                    if recursive and item.is_dir() and current_depth < max_depth and total_items_collected < max_items:
                        subdirectory_result = scan_directory(item, current_depth + 1)
                        # Only include subdirectory contents if they're not empty
                        if subdirectory_result["items"]:
                            item_info["contents"] = subdirectory_result["items"]
                            item_info["subdirectory_count"] = subdirectory_result["directory_count"]
                            item_info["subfile_count"] = subdirectory_result["file_count"]
                    
                    items.append(item_info)
                    total_items_collected += 1
                    
            except PermissionError:
                pass  # Skip directories we can't access
            
            # Sort items: directories first, then files, both alphabetically
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return {
                "items": items,
                "directory_count": sum(1 for item in items if item["type"] == "directory"),
                "file_count": sum(1 for item in items if item["type"] == "file")
            }
        
        result = scan_directory(directory_path)
        
        response = {
            "directory_path": str(directory_path),
            "items": result["items"],
            "total_directories": result["directory_count"],
            "total_files": result["file_count"],
            "total_items": len(result["items"]),
            "filters": {
                "include_hidden": include_hidden,
                "recursive": recursive,
                "max_depth": max_depth,
                "file_extensions": file_extensions,
                "max_items": max_items
            },
            "status": "success"
        }
        
        # Add truncation warning if needed
        if truncated:
            response["truncated"] = True
            response["warning"] = f"Results truncated to {max_items} items for token efficiency. Use more specific filters or search_files for better results."
        
        return response
        
    except PermissionError:
        return {
            "error": f"Permission denied accessing directory: {directory_path}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: list_directory failed: {str(e)}")
        return {
            "error": f"Failed to list directory: {str(e)}",
            "status": "error"
        }

async def get_file_info(
    file_path: str
) -> Dict[str, Any]:
    """
    Get detailed information about a file without reading its content.
    
    Args:
        file_path: Path to the file to inspect (supports ~ for home directory) (required)
    
    Returns:
        Dictionary containing file metadata
    """
    print(f"INFO: get_file_info called with path: {file_path}")
    
    try:
        file_path = _expand_path(file_path)
        
        if not file_path.exists():
            return {
                "error": f"File does not exist: {file_path}",
                "status": "error"
            }
        
        stat = file_path.stat()
        
        return {
            "file_path": str(file_path),
            "name": file_path.name,
            "extension": file_path.suffix.lower(),
            "parent_directory": str(file_path.parent),
            "type": "directory" if file_path.is_dir() else "file",
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 3),
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "accessed_time": stat.st_atime,
            "created_time_readable": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed_time_readable": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "is_readable": os.access(file_path, os.R_OK),
            "is_writable": os.access(file_path, os.W_OK),
            "is_executable": os.access(file_path, os.X_OK),
            "status": "success"
        }
        
    except PermissionError:
        return {
            "error": f"Permission denied accessing: {file_path}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: get_file_info failed: {str(e)}")
        return {
            "error": f"Failed to get file info: {str(e)}",
            "status": "error"
        }

async def search_files(
    search_directory: str,
    filename_pattern: Optional[str] = None,
    content_pattern: Optional[str] = None,
    file_extensions: Optional[List[str]] = None,
    max_files: int = 50,  # CHANGED: Reduced from 100 to 50
    max_file_size_mb: int = 10,
    max_search_depth: int = 3  # NEW: Limit search depth
) -> Dict[str, Any]:
    """
    Search for files by name pattern or content within a directory with token-efficient limits.
    
    Args:
        search_directory: Directory to search in (supports ~ for home directory) (required)
        filename_pattern: Pattern to match in filenames (case-insensitive) (optional)
        content_pattern: Pattern to search for in file contents (case-insensitive) (optional)
        file_extensions: File extensions to include, e.g., [".txt", ".py"] (optional)
        max_files: Maximum number of files to return (default: 50, max: 100)
        max_file_size_mb: Maximum file size to search content in MB (default: 10)
        max_search_depth: Maximum directory depth to search (default: 3, max: 5)
    
    Returns:
        Dictionary containing search results
    """
    print(f"INFO: search_files called in directory: {search_directory}")
    
    # Enforce limits for token efficiency
    max_files = min(max_files, 100)
    max_search_depth = min(max_search_depth, 5)
    
    try:
        search_directory = _expand_path(search_directory)
        
        if not search_directory.exists() or not search_directory.is_dir():
            return {
                "error": f"Search directory does not exist or is not a directory: {search_directory}",
                "status": "error"
            }
        
        matching_files = []
        searched_files = 0
        max_size_bytes = max_file_size_mb * 1024 * 1024
        truncated = False
        
        def search_in_directory(directory: Path, current_depth: int = 0):
            nonlocal matching_files, searched_files, truncated
            
            if current_depth > max_search_depth or len(matching_files) >= max_files:
                if len(matching_files) >= max_files:
                    truncated = True
                return
            
            try:
                for item in directory.iterdir():
                    if len(matching_files) >= max_files:
                        truncated = True
                        break
                    
                    if item.is_file():
                        # Filter by file extensions
                        if file_extensions and not any(item.name.lower().endswith(ext.lower()) for ext in file_extensions):
                            continue
                        
                        searched_files += 1
                        match_info = {
                            "file_path": str(item),
                            "filename": item.name,
                            "relative_path": str(item.relative_to(search_directory)),
                            "size_bytes": item.stat().st_size,
                            "matched_by": []
                        }
                        
                        # Check filename pattern
                        filename_match = False
                        if filename_pattern:
                            if filename_pattern.lower() in item.name.lower():
                                filename_match = True
                                match_info["matched_by"].append("filename")
                        
                        # Check content pattern
                        content_match = False
                        if content_pattern and item.stat().st_size <= max_size_bytes:
                            try:
                                with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if content_pattern.lower() in content.lower():
                                        content_match = True
                                        match_info["matched_by"].append("content")
                            except:
                                pass  # Skip files that can't be read
                        
                        # Add to results if any pattern matched (or no patterns specified)
                        if (not filename_pattern and not content_pattern) or filename_match or content_match:
                            matching_files.append(match_info)
                    
                    elif item.is_dir() and current_depth < max_search_depth:
                        try:
                            search_in_directory(item, current_depth + 1)
                        except PermissionError:
                            pass  # Skip directories we can't access
            except PermissionError:
                pass  # Skip directories we can't access
        
        search_in_directory(search_directory)
        
        response = {
            "search_directory": str(search_directory),
            "search_criteria": {
                "filename_pattern": filename_pattern,
                "content_pattern": content_pattern,
                "file_extensions": file_extensions,
                "max_file_size_mb": max_file_size_mb,
                "max_search_depth": max_search_depth
            },
            "matching_files": matching_files,
            "total_matches": len(matching_files),
            "files_searched": searched_files,
            "max_files_limit": max_files,
            "status": "success"
        }
        
        if truncated:
            response["truncated"] = True
            response["warning"] = f"Search truncated at {max_files} results for token efficiency. Use more specific patterns to narrow results."
        
        return response
        
    except Exception as e:
        print(f"ERROR: search_files failed: {str(e)}")
        return {
            "error": f"Search failed: {str(e)}",
            "status": "error"
        }

async def find_directory(
    directory_name: str,
    search_root: str = "~",
    max_results: int = 10,
    max_search_depth: int = 3
) -> Dict[str, Any]:
    """
    Find directories by name pattern - optimized for token efficiency.
    This is much more efficient than recursive list_directory for finding specific directories.
    
    Args:
        directory_name: Name or pattern to search for in directory names (case-insensitive) (required)
        search_root: Root directory to start search from (default: "~" for home directory)
        max_results: Maximum number of matching directories to return (default: 10, max: 20)
        max_search_depth: Maximum directory depth to search (default: 3, max: 5)
    
    Returns:
        Dictionary containing matching directories
    """
    print(f"INFO: find_directory called searching for: {directory_name}")
    
    # Enforce limits for token efficiency
    max_results = min(max_results, 20)
    max_search_depth = min(max_search_depth, 5)
    
    try:
        search_root = _expand_path(search_root)
        
        if not search_root.exists() or not search_root.is_dir():
            return {
                "error": f"Search root does not exist or is not a directory: {search_root}",
                "status": "error"
            }
        
        matching_directories = []
        searched_directories = 0
        
        def search_for_directories(directory: Path, current_depth: int = 0):
            nonlocal matching_directories, searched_directories
            
            if current_depth > max_search_depth or len(matching_directories) >= max_results:
                return
            
            try:
                for item in directory.iterdir():
                    if len(matching_directories) >= max_results:
                        break
                    
                    if item.is_dir():
                        searched_directories += 1
                        
                        # Check if directory name matches pattern
                        if directory_name.lower() in item.name.lower():
                            stat = item.stat()
                            matching_directories.append({
                                "directory_name": item.name,
                                "full_path": str(item),
                                "relative_path": str(item.relative_to(search_root)),
                                "parent_directory": str(item.parent),
                                "modified_time": stat.st_mtime,
                                "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                "depth": current_depth
                            })
                        
                        # Continue searching in subdirectories
                        if current_depth < max_search_depth:
                            search_for_directories(item, current_depth + 1)
                            
            except PermissionError:
                pass  # Skip directories we can't access
        
        search_for_directories(search_root)
        
        return {
            "search_pattern": directory_name,
            "search_root": str(search_root),
            "matching_directories": matching_directories,
            "total_matches": len(matching_directories),
            "directories_searched": searched_directories,
            "search_criteria": {
                "max_results": max_results,
                "max_search_depth": max_search_depth
            },
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: find_directory failed: {str(e)}")
        return {
            "error": f"Directory search failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the read-only file system tools with the MCP server"""
    mcp_instance.tool()(get_system_info)
    mcp_instance.tool()(read_file)
    mcp_instance.tool()(list_directory)
    mcp_instance.tool()(get_file_info)
    mcp_instance.tool()(search_files)
    mcp_instance.tool()(find_directory)  # NEW: Efficient directory finder
    print("INFO: Read-only file system tools registered successfully")