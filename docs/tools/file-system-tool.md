# File System Tools Documentation

Tools for reading and exploring the local file system with read-only access and security controls.

## Overview

The File System tools provide AI agents with safe, read-only access to the local file system. These tools enable file exploration, content reading, and file searching while maintaining security through size limits and permission controls.

## Installation Requirements

No external dependencies required. Uses built-in Python functionality.

## Environment Variables

None required. Tools operate with local file system permissions.

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

### Directory Operations

#### `list_directory`
Lists directory contents with comprehensive filtering and organization options.

**What it does:**
- Lists files and subdirectories with detailed metadata
- Supports recursive directory traversal with depth control
- Filters by file extensions and hidden file visibility
- Provides file sizes, timestamps, and type information
- Sorts results logically (directories first, then alphabetically)

**Parameters:**
- `directory_path` (required) - Directory to list (supports ~ for home directory)
- `include_hidden` (optional) - Include hidden files/directories (default: False)
- `recursive` (optional) - List subdirectories recursively (default: False)
- `max_depth` (optional) - Maximum recursion depth (default: 3)
- `file_extensions` (optional) - Filter by extensions, e.g., [".txt", ".py"]

**Returns:**
- Complete directory listing with metadata
- File and directory counts
- Size information and timestamps
- Relative paths and file extensions

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

### File Search

#### `search_files`
Searches for files by filename patterns or content within directories.

**What it does:**
- Searches recursively through directory trees
- Matches filename patterns (case-insensitive)
- Searches file content for text patterns
- Filters by file extensions and size limits
- Provides match type indicators

**Parameters:**
- `search_directory` (required) - Directory to search (supports ~ for home directory)
- `filename_pattern` (optional) - Text to match in filenames
- `content_pattern` (optional) - Text to search for in file contents
- `file_extensions` (optional) - Extensions to include, e.g., [".txt", ".py"]
- `max_files` (optional) - Maximum results to return (default: 100)
- `max_file_size_mb` (optional) - Max file size for content search (default: 10)

**Returns:**
- List of matching files with paths and metadata
- Match indicators (filename, content, or both)
- Search statistics and criteria used
- Relative paths from search directory

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

## Security Features

### Read-Only Access
- No file writing, deletion, or modification capabilities
- Cannot create directories or change permissions
- Safe exploration without system modification risk

### Size Limitations
- Default 50MB limit for file reading
- Configurable limits for content searching
- Prevents memory exhaustion from large files

### Permission Respect
- Honors file system permissions
- Gracefully handles access denied scenarios
- Reports permission status in file information

### Path Validation
- Prevents directory traversal attacks
- Resolves all paths to absolute locations
- Validates file and directory existence

## Use Cases

### Development and Debugging
- Explore project directory structures
- Read configuration files and logs
- Search for specific code patterns or files
- Analyze file organization and dependencies

### Content Analysis
- Read text files for processing
- Search documents for specific information
- Analyze file metadata and organization
- Extract content for further processing

### System Administration
- Explore system directories and configurations
- Find files by name or content patterns
- Analyze disk usage and file organization
- Monitor file timestamps and changes

### Data Processing
- Read CSV, JSON, and text data files
- Search through document collections
- Analyze file structures for data migration
- Extract information from various file formats

## Common Workflows

### Initial System Exploration
1. **Get system info** - Understand your environment
2. **List home directory** - See your main folders
3. **Explore specific directories** - Navigate to areas of interest

### File Research
1. **Search by filename** - Find files with specific names
2. **Search by content** - Locate files containing text
3. **Get file details** - Examine metadata before reading
4. **Read file content** - Extract information for analysis

### Project Analysis
1. **List project directory** - See overall structure
2. **Filter by file types** - Focus on specific extensions
3. **Search for patterns** - Find specific code or text
4. **Read key files** - Examine important documents

## Error Handling

### Common Error Types
- **File Not Found**: Invalid paths or missing files
- **Permission Denied**: Insufficient access rights
- **File Too Large**: Exceeds size limits for reading
- **Encoding Errors**: Binary files read as text

### Graceful Degradation
- Continues operation when some files are inaccessible
- Provides detailed error messages for troubleshooting
- Skips problematic files in directory listings
- Offers alternative approaches (e.g., base64 for binary files)

## Integration Patterns

### With Web Search
- Save search results to analyze local files
- Cross-reference online information with local documents
- Build research databases from local and web sources

### With Airtable
- Read local data files to populate databases
- Export file metadata to structured tables
- Create file catalogs and organization systems

### With Google Workspace
- Read local files to create cloud documents
- Analyze local content for presentation creation
- Import local data into spreadsheets

### With Browser Automation
- Read local HTML files for web testing
- Process downloaded files from web automation
- Analyze scraped content stored locally

## Best Practices

### Performance Optimization
- Use file extensions filtering to reduce processing
- Set appropriate size limits for content searches
- Limit recursion depth for large directory trees
- Use specific patterns rather than broad searches

### Security Considerations
- Never run with elevated privileges unless necessary
- Be cautious with recursive operations on large directories
- Validate paths before processing
- Monitor file access patterns for unusual activity

### Workflow Efficiency
- Start with `get_system_info` to understand environment
- Use `list_directory` to explore before detailed operations
- Combine filename and content searches for precision
- Cache file information for repeated operations

## Technical Specifications

### Supported File Types
- **Text Files**: Any encoding supported by Python
- **Binary Files**: Via base64 encoding
- **Archives**: Can read as binary but not extract
- **Images**: Can read metadata and binary content

### Path Formats
- **Absolute**: `/full/path/to/file` or `C:\full\path\to\file`
- **Relative**: `./relative/path` or `relative\path`
- **Home-relative**: `~/Documents/file.txt`
- **Environment**: `$HOME/file` or `%USERPROFILE%\file`

### Performance Characteristics
- **Directory Listing**: Fast for most directories
- **File Reading**: Limited by disk I/O and file size
- **Content Search**: CPU-intensive for large files
- **Recursive Operations**: Can be slow for deep hierarchies

### Memory Usage
- **File Reading**: Loads entire file into memory
- **Directory Listing**: Minimal memory usage
- **Search Operations**: Processes files individually
- **Large Files**: Automatic rejection prevents memory issues