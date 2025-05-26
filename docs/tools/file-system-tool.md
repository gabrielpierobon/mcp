# File System Tools Documentation

Tools for reading and exploring the local file system with read-only access, security controls, and token-efficient operations.

## Overview

The File System tools provide AI agents with safe, read-only access to the local file system. These tools enable file exploration, content reading, and file searching while maintaining security through size limits, permission controls, and **token-efficient response limits** to prevent expensive API calls.

## Installation Requirements

No external dependencies required. Uses built-in Python functionality.

## Environment Variables

None required. Tools operate with local file system permissions.

## 🚀 New Token-Efficient Features

### Smart Limits
- **Default max_depth**: 1 (prevents deep recursion)
- **Item limits**: 50 items per request (max 100)
- **Search limits**: Focused results for cost efficiency
- **Truncation warnings**: Clear feedback when limits are hit

### New Tool: `find_directory`
- **Purpose-built**: For finding directories by name pattern
- **Token-efficient**: Returns only matching directories, not contents
- **Much faster**: Than recursive directory listing

## Available Functions

### System Information

#### `get_system_info`
Provides comprehensive information about the current system and user environment.

**What it does:**
- Identifies operating system and platform details
- Shows user home directory and current working directory
- Lists common directories (Desktop, Documents, Downloads, etc.)
- Displays username and system-specific paths
- Shows path separator for the current OS

**Parameters:**
None required.

**Returns:**
- System type (Windows, Linux, macOS) and platform details
- Home directory path and current working directory
- Username and common directory locations
- Available directories that actually exist on the system

**Token Impact:** ~20-50 tokens (very efficient)

### File Reading

#### `read_file`
Reads content from files with encoding support and size limitations.

**What it does:**
- Reads text files with specified encoding
- Supports binary files via base64 encoding
- Enforces file size limits for safety
- Provides file metadata and timestamps
- Handles various text encodings

**Parameters:**
- `file_path` (required) - Path to file (supports ~ for home directory)
- `encoding` (optional) - Text encoding (default: "utf-8")
- `return_base64` (optional) - Return binary content as base64 (default: False)
- `max_size_mb` (optional) - Maximum file size in MB (default: 50)

**Returns:**
- File content as text or base64
- File size in bytes and MB
- Modified timestamp (raw and readable format)
- Content type and encoding information

**Token Impact:** Varies by file size, but capped at 50MB

### Directory Operations

#### `list_directory` ⚡ **IMPROVED**
Lists directory contents with comprehensive filtering and **token-efficient controls**.

**What it does:**
- Lists files and subdirectories with detailed metadata
- **NEW**: Enforces strict token limits for cost efficiency
- **NEW**: Truncates results with clear warnings
- Supports recursive directory traversal with **reduced depth limits**
- Filters by file extensions and hidden file visibility
- Provides file sizes, timestamps, and type information
- Sorts results logically (directories first, then alphabetically)

**Parameters:**
- `directory_path` (required) - Directory to list (supports ~ for home directory)
- `include_hidden` (optional) - Include hidden files/directories (default: False)
- `recursive` (optional) - List subdirectories recursively (default: False)
- `max_depth` (optional) - Maximum recursion depth (default: 1, **max: 2**)
- `file_extensions` (optional) - Filter by extensions, e.g., [".txt", ".py"]
- `max_items` (optional) - **NEW**: Maximum total items to return (default: 50, **max: 100**)

**Returns:**
- Complete directory listing with metadata
- File and directory counts
- Size information and timestamps
- Relative paths and file extensions
- **NEW**: Truncation warnings when limits are hit

**Token Impact:** ~50-200 tokens (non-recursive), ~200-500 tokens (recursive with limits)

**⚠️ Important Changes:**
- **Default depth reduced** from 3 to 1
- **Hard limits enforced** - cannot exceed max_depth=2 or max_items=100
- **Truncation warnings** when results are cut off
- **Much more efficient** than previous version

#### `get_file_info`
Retrieves detailed metadata about files and directories without reading content.

**What it does:**
- Provides comprehensive file metadata
- Shows creation, modification, and access timestamps
- Displays file permissions (readable, writable, executable)
- Calculates file sizes in multiple formats
- Identifies file types and extensions

**Parameters:**
- `file_path` (required) - Path to inspect (supports ~ for home directory)

**Returns:**
- Complete file metadata including all timestamps
- File permissions and accessibility information
- Parent directory and file extension details
- Size information in bytes and MB

**Token Impact:** ~30-50 tokens (very efficient)

### File Search

#### `search_files` ⚡ **IMPROVED**
Searches for files by filename patterns or content within directories with **enhanced limits**.

**What it does:**
- Searches recursively through directory trees
- Matches filename patterns (case-insensitive)
- Searches file content for text patterns
- **NEW**: Enforced limits for token efficiency
- Filters by file extensions and size limits
- Provides match type indicators

**Parameters:**
- `search_directory` (required) - Directory to search (supports ~ for home directory)
- `filename_pattern` (optional) - Text to match in filenames
- `content_pattern` (optional) - Text to search for in file contents
- `file_extensions` (optional) - Extensions to include, e.g., [".txt", ".py"]
- `max_files` (optional) - Maximum results to return (default: 50, **max: 100**)
- `max_file_size_mb` (optional) - Max file size for content search (default: 10)
- `max_search_depth` (optional) - **NEW**: Maximum directory depth (default: 3, **max: 5**)

**Returns:**
- List of matching files with paths and metadata
- Match indicators (filename, content, or both)
- Search statistics and criteria used
- Relative paths from search directory
- **NEW**: Truncation warnings when results are limited

**Token Impact:** ~100-500 tokens (with limits enforced)

#### `find_directory` 🆕 **NEW**
Efficiently finds directories by name pattern - **optimized for token efficiency**.

**What it does:**
- **Purpose-built** for finding directories by name
- **Much more efficient** than recursive `list_directory`
- Searches by name pattern (case-insensitive)
- Returns only matching directories, not their contents
- Provides path information and metadata

**Parameters:**
- `directory_name` (required) - Name or pattern to search for (case-insensitive)
- `search_root` (optional) - Root directory to start from (default: "~")
- `max_results` (optional) - Maximum directories to return (default: 10, **max: 20**)
- `max_search_depth` (optional) - Maximum search depth (default: 3, **max: 5**)

**Returns:**
- List of matching directories with full paths
- Relative paths from search root
- Directory metadata (modified time, etc.)
- Search statistics and criteria

**Token Impact:** ~30-150 tokens (very efficient)

**Use Cases:**
- Finding project directories: `find_directory("my_project")`
- Locating specific folders: `find_directory("Documents")`
- Searching for directories: `find_directory("node_modules", "~/projects")`

## Path Support Features

### Tilde Expansion
All functions support `~` notation for user home directory:
- `"~"` - User home directory
- `"~/Documents"` - Documents folder
- `"~/Desktop/myfile.txt"` - File on desktop

### Environment Variables
Automatic expansion of environment variables:
- Windows: `%USERPROFILE%`, `%APPDATA%`
- Linux/macOS: `$HOME`, `$USER`

### Cross-Platform Compatibility
- Handles Windows, Linux, and macOS path conventions
- Automatically uses correct path separators
- Resolves relative and absolute paths

## 🎯 Best Practices for Token Efficiency

### 1. **Start with Overview Tools**
```python
# Get system information first (minimal tokens)
get_system_info()

# Check specific common directories
list_directory("~/Documents")  # Non-recursive, efficient
```

### 2. **Use find_directory for Directory Discovery**
```python
# ✅ GOOD: Find specific directories efficiently
find_directory("agent_playground", search_root="~")
find_directory("project", search_root="~/Documents")

# ❌ AVOID: Recursive listing to find directories
# list_directory("~", recursive=True)  # Expensive!
```

### 3. **Layer Your Exploration**
```python
# Step 1: Find the directory
result = find_directory("demo")

# Step 2: List its contents specifically
if result["matching_directories"]:
    demo_path = result["matching_directories"][0]["full_path"]
    list_directory(demo_path)  # Focused, efficient
```

### 4. **Use Filters Aggressively**
```python
# Filter by file type
list_directory("~/projects", file_extensions=[".py", ".js", ".json"])

# Limit results
search_files("~/code", filename_pattern="config", max_files=20)
```

## Security Features

### Read-Only Access
- No file writing, deletion, or modification capabilities
- Cannot create directories or change permissions
- Safe exploration without system modification risk

### Size Limitations
- Default 50MB limit for file reading
- Configurable limits for content searching
- **NEW**: Item count limits prevent token explosions

### Permission Respect
- Honors file system permissions
- Gracefully handles access denied scenarios
- Reports permission status in file information

### Path Validation
- Prevents directory traversal attacks
- Resolves all paths to absolute locations
- Validates file and directory existence

## Token Efficiency Comparison

### Before (Problematic)
```python
list_directory("~", recursive=True, max_depth=3)
# Result: 10,000-50,000 tokens 💸
```

### After (Efficient)
```python
# Find specific directory
find_directory("target_folder")  # ~100 tokens ✅

# List its contents
list_directory("~/target_folder")  # ~200 tokens ✅

# Total: ~300 tokens vs 50,000 tokens = 99.4% savings!
```

## Use Cases

### Development and Debugging
- Explore project directory structures efficiently
- Find configuration files quickly
- Search for specific code patterns
- Analyze file organization with controlled output

### Content Analysis
- Read text files for processing
- Search documents for specific information
- Analyze file metadata and organization
- Extract content for further processing

### System Administration
- Explore system directories safely
- Find files by name or content patterns
- Analyze disk usage with limits
- Monitor file timestamps and changes

### Project Discovery
- **NEW**: Find project directories by name
- Locate specific folders quickly
- Navigate to target directories efficiently
- Avoid expensive recursive scans

## Common Workflows

### Initial System Exploration
```python
# 1. Get system overview
system_info = get_system_info()

# 2. Check common directories
list_directory(system_info["common_directories"]["documents"])

# 3. Find specific items
find_directory("my_project")
```

### Finding and Exploring Projects
```python
# 1. Find project directory efficiently
projects = find_directory("demo", search_root="~/agent_playground")

# 2. Get project structure
if projects["matching_directories"]:
    project_path = projects["matching_directories"][0]["full_path"]
    list_directory(project_path, file_extensions=[".html", ".css", ".js"])
```

### File Research with Limits
```python
# 1. Search for specific files
configs = search_files("~/projects", 
                      filename_pattern="config",
                      file_extensions=[".json", ".yaml"],
                      max_files=10)  # Limited results

# 2. Read specific files
for config in configs["matching_files"][:3]:  # Only first 3
    read_file(config["file_path"])
```

## Error Handling

### Common Error Types
- **File Not Found**: Invalid paths or missing files
- **Permission Denied**: Insufficient access rights
- **File Too Large**: Exceeds size limits for reading
- **Results Truncated**: **NEW**: Too many items, results limited
- **Encoding Errors**: Binary files read as text

### Graceful Degradation
- Continues operation when some files are inaccessible
- Provides detailed error messages for troubleshooting
- Skips problematic files in directory listings
- **NEW**: Clear truncation warnings with suggestions
- Offers alternative approaches (e.g., `find_directory` vs `list_directory`)

### **NEW**: Truncation Handling
When results are truncated, tools provide:
- Clear warning messages
- Suggestions for more specific filtering
- Current limits and maximums
- Alternative tool recommendations

## Migration Guide

### If You Were Using Recursive Listing
```python
# OLD (expensive)
list_directory("~", recursive=True, max_depth=3)

# NEW (efficient)
# Step 1: Find what you're looking for
find_directory("target_name")

# Step 2: List specific directories
list_directory("~/specific/path")
```

### If You Need Deep Exploration
```python
# Instead of one big recursive call:
# OLD: list_directory("~", recursive=True)

# NEW: Progressive exploration
get_system_info()  # Get common paths
find_directory("project_name")  # Find specific directories
list_directory("~/found/path", max_items=30)  # Targeted listing
```

## Performance Characteristics

### Token Usage Guidelines
- **get_system_info()**: 20-50 tokens ⚡
- **find_directory()**: 30-150 tokens ⚡
- **get_file_info()**: 30-50 tokens ⚡
- **list_directory() (non-recursive)**: 50-200 tokens ✅
- **search_files() (filtered)**: 100-500 tokens ⚠️
- **list_directory() (recursive, old)**: 5,000-50,000 tokens ❌

### Performance Targets
- **Target**: <500 tokens per file system operation
- **Warning**: >1000 tokens (review approach)
- **Critical**: >5000 tokens (use different strategy)

### Memory Usage
- **File Reading**: Loads entire file into memory (capped at 50MB)
- **Directory Listing**: Minimal memory with item limits
- **Search Operations**: Processes files individually with limits
- **Large Directories**: Automatic truncation prevents memory issues

## Integration Patterns

### With Web Search
- Save search results to analyze local files
- Cross-reference online information with local documents
- Build research databases from local and web sources

### With File Writing Tools
- Read existing files to create new versions
- Analyze project structures before creating new projects
- Copy patterns from existing code

### With Airtable
- Read local data files to populate databases
- Export file metadata to structured tables
- Create file catalogs and organization systems

### With Google Workspace
- Read local files to create cloud documents
- Analyze local content for presentation creation
- Import local data into spreadsheets

## Best Practices Summary

### ✅ **DO**
- Start with `get_system_info()` for overview
- Use `find_directory()` to locate specific directories
- Apply `file_extensions` filters when possible
- Use `max_items` limits for large directories
- Layer your exploration (overview → specific → detailed)
- Check for `"truncated"` warnings in responses

### ❌ **DON'T**
- Use `list_directory("~", recursive=True)` without limits
- Search entire system with `search_files("/")`
- Ignore truncation warnings
- Request unlimited results from large directories
- Use recursive listing to find specific items

### 🎯 **PREFERRED PATTERNS**
```python
# Finding directories
find_directory("target_name") → list_directory("specific_path")

# Exploring projects  
get_system_info() → find_directory("project") → list_directory(project_path)

# Searching files
search_files(specific_path, pattern, max_files=20) → read_file(results)
```

## Troubleshooting

### Large Token Responses
If you're still getting large responses:
1. Check if `recursive=True` - set to `False`
2. Use `max_items` parameter to limit results
3. Apply `file_extensions` filters
4. Use `find_directory()` instead of recursive listing
5. Break large requests into smaller, targeted ones

### "Truncated" Warnings
When you see truncation warnings:
1. Use more specific `file_extensions` filters
2. Reduce `max_items` or `max_files` parameters
3. Search in more specific directories
4. Use `find_directory()` for directory discovery

### Finding Specific Items
For finding directories or files:
1. Use `find_directory()` for directories
2. Use `search_files()` with specific patterns
3. Avoid broad recursive scans
4. Start with system common directories

The updated file system tools provide the same functionality with dramatic improvements in token efficiency, making them much more cost-effective for API usage while maintaining full exploration capabilities.