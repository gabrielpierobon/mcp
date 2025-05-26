# File Writing Tools Documentation

Tools for creating and writing files within a secure sandbox directory.

## Overview

The File Writing tools provide AI agents with the ability to create directories and write files within a restricted playground area: `C:\Users\usuario\agent_playground`. These tools are designed to be safe by limiting all file operations to this specific directory.

## Installation Requirements

No external dependencies required. Uses built-in Python functionality.

## Environment Variables

None required. The playground directory is hardcoded for security.

## Sandbox Security

### Playground Directory
- **Root Path**: `C:\Users\usuario\agent_playground`
- **Automatic Creation**: Directory is created if it doesn't exist
- **Path Validation**: All operations are restricted to this directory tree
- **No Escaping**: Path traversal attacks (../) are prevented

### Safety Features
- **Directory Restriction**: Cannot write outside the playground
- **Path Validation**: All paths are validated before operation
- **Overwrite Control**: Configurable file overwriting behavior
- **Error Handling**: Comprehensive error reporting

## Available Functions

### File Operations

#### `write_file`
Creates or overwrites files with specified content.

**What it does:**
- Writes text content to files with specified encoding
- Creates parent directories automatically if needed
- Validates all paths are within the playground
- Supports both relative and absolute paths (within playground)
- Provides detailed operation feedback

**Parameters:**
- `file_path` (required) - Path to file (relative to playground or absolute within playground)
- `content` (required) - Text content to write
- `encoding` (optional) - Text encoding (default: "utf-8")
- `create_directories` (optional) - Create parent dirs (default: True)
- `overwrite` (optional) - Allow overwriting existing files (default: True)

**Returns:**
- File path relative to playground
- Content length and file size information
- Operation timestamps and encoding used
- Success/error status

**Examples:**
```python
# Relative path (creates C:\Users\usuario\agent_playground\my_script.py)
write_file("my_script.py", "print('Hello World!')")

# Nested path (creates directories automatically)
write_file("projects/web/index.html", "<html>...</html>")

# Absolute path within playground
write_file("C:/Users/usuario/agent_playground/config.json", "{...}")
```

#### `create_directory`
Creates directories within the playground.

**What it does:**
- Creates directories and all necessary parent directories
- Validates paths are within the playground
- Handles existing directories gracefully
- Returns creation status and path information

**Parameters:**
- `directory_path` (required) - Path to directory to create

**Returns:**
- Directory path relative to playground
- Creation status and absolute path
- Success/error status

#### `write_multiple_files`
Writes multiple files in a single operation for efficiency.

**What it does:**
- Batch writes multiple files with individual configuration
- Provides detailed results for each file operation
- Continues processing even if some files fail
- Returns comprehensive success/failure statistics

**Parameters:**
- `files` (required) - List of file dictionaries with 'path' and 'content' keys

**Format:**
```python
files = [
    {
        "path": "src/main.py",
        "content": "#!/usr/bin/env python3\nprint('Hello!')",
        "encoding": "utf-8"  # optional
    },
    {
        "path": "README.md", 
        "content": "# My Project\n\nDescription here."
    }
]
```

### Project Creation

#### `create_project_structure`
Creates complete project structures with templates for common project types.

**What it does:**
- Sets up directory structures for different project types
- Creates template files with proper content
- Supports custom additional files
- Provides multiple project type templates

**Parameters:**
- `project_name` (required) - Name of the project (used as root directory)
- `project_type` (optional) - Project template type (default: "general")
- `files` (optional) - Additional custom files to create

**Available Project Types:**

**Web Project** (`project_type="web"`)
- Creates: `index.html`, `css/style.css`, `js/script.js`, `README.md`
- Directories: `css/`, `js/`, `images/`, `assets/`
- Includes: Basic HTML structure, CSS reset, JavaScript starter

**Python Project** (`project_type="python"`)
- Creates: `main.py`, `requirements.txt`, `tests/test_main.py`, `README.md`
- Directories: `src/`, `tests/`, `docs/`, `data/`
- Includes: Main entry point, test structure, package setup

**React Project** (`project_type="react"`)
- Creates: `package.json`, `public/index.html`, `src/App.js`, `src/index.js`
- Directories: `src/`, `public/`, `src/components/`, `src/styles/`
- Includes: React setup, component structure, styling files

**General Project** (`project_type="general"`)
- Creates: `README.md`, `notes.txt`, `scripts/setup.py`
- Directories: `docs/`, `scripts/`, `data/`
- Includes: Basic project documentation and structure

### Utility Functions

#### `get_playground_info`
Provides information about the playground directory and its contents.

**What it does:**
- Shows playground directory status and permissions
- Counts total files and directories
- Displays creation and modification times
- Provides access permission information

**Returns:**
- Playground root path and existence status
- File and directory counts
- Timestamp information
- Permission details (readable, writable, executable)

## Path Handling

### Supported Path Formats

**Relative Paths** (recommended):
- `"my_file.txt"` → `C:\Users\usuario\agent_playground\my_file.txt`
- `"projects/web/index.html"` → `C:\Users\usuario\agent_playground\projects\web\index.html`
- `"scripts/setup.py"` → `C:\Users\usuario\agent_playground\scripts\setup.py`

**Absolute Paths** (within playground only):
- `"C:/Users/usuario/agent_playground/config.json"` → Valid
- `"C:\\Users\\usuario\\agent_playground\\data\\file.csv"` → Valid
- `"C:/Users/usuario/Documents/file.txt"` → **REJECTED** (outside playground)

**Cross-Platform Support:**
- Forward slashes (`/`) work on all platforms
- Backslashes (`\`) work on Windows
- Path resolution handles platform differences automatically

### Path Validation Rules

1. **Sandbox Enforcement**: All paths must resolve to within the playground directory
2. **Traversal Prevention**: `../` patterns are resolved and validated
3. **Absolute Path Checking**: Absolute paths are only allowed within playground
4. **Automatic Resolution**: Relative paths are made relative to playground root

## File Type Support

### Text Files
All text-based files with any encoding:
- **Source Code**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.php`
- **Configuration**: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.env`
- **Documentation**: `.md`, `.txt`, `.rst`, `.org`
- **Data**: `.csv`, `.tsv`, `.xml`, `.sql`
- **Scripts**: `.sh`, `.bat`, `.ps1`

### Content Types
- **UTF-8**: Default encoding for most files
- **ASCII**: Simple text files
- **Latin-1**: Legacy encoding support
- **Custom Encodings**: Configurable per file

### File Naming
- **Case Sensitive**: File names preserve case
- **Special Characters**: Most characters allowed except path separators
- **Extensions**: Any file extension supported
- **No Extension**: Files without extensions are allowed

## Use Cases

### Development Projects
- **Web Development**: Create HTML, CSS, JavaScript projects
- **Python Development**: Set up Python packages with proper structure
- **React Applications**: Generate React project templates
- **Script Collections**: Organize utility scripts and tools

### Content Creation
- **Documentation**: Write README files, guides, and manuals
- **Configuration**: Create config files for applications
- **Data Files**: Generate CSV, JSON, XML data files
- **Templates**: Create reusable project templates

### Automation and Scripting
- **Build Scripts**: Create build and deployment scripts
- **Data Processing**: Generate data transformation scripts
- **Test Files**: Create test cases and sample data
- **Utility Scripts**: Build automation and helper scripts

### Rapid Prototyping
- **Quick Projects**: Fast project structure creation
- **Experimentation**: Safe environment for testing ideas
- **Learning**: Practice project setup and organization
- **Demonstrations**: Create example projects and tutorials

## Integration Patterns

### With Web Search Tools
```python
# Research and document findings
search_results = await brave_web_search("React best practices")
documentation = format_research(search_results)
await write_file("research/react_best_practices.md", documentation)
```

### With Web Crawling
```python
# Extract content and save locally
content = await crawl_webpage("https://example.com/tutorial")
await write_file("tutorials/extracted_tutorial.md", content['markdown'])
```

### With File System Reading
```python
# Read existing file and create new version
existing = await read_file("~/Documents/config.json")
modified_config = modify_config(existing['content'])
await write_file("configs/new_config.json", modified_config)
```

### With Calculator and Data
```python
# Generate data files with calculations
data = generate_calculations()
csv_content = format_as_csv(data)
await write_file("data/calculations.csv", csv_content)
```

## Common Workflows

### Creating a Web Project
```python
# 1. Create project structure
await create_project_structure("my-website", "web")

# 2. Add custom files
await write_file("my-website/js/utils.js", "// Utility functions")

# 3. Update content
await write_file("my-website/index.html", custom_html_content)
```

### Python Package Development
```python
# 1. Create Python project
await create_project_structure("my-package", "python")

# 2. Add modules
await write_multiple_files([
    {"path": "my-package/src/utils.py", "content": utility_code},
    {"path": "my-package/src/main.py", "content": main_code},
    {"path": "my-package/tests/test_utils.py", "content": test_code}
])
```

### Documentation Generation
```python
# 1. Create documentation structure
await create_directory("docs/api")
await create_directory("docs/guides")

# 2. Generate documentation files
await write_multiple_files([
    {"path": "docs/README.md", "content": overview_content},
    {"path": "docs/api/functions.md", "content": api_docs},
    {"path": "docs/guides/getting-started.md", "content": guide_content}
])
```

### Configuration Management
```python
# 1. Create config directory
await create_directory("configs")

# 2. Generate different environment configs
environments = ["development", "staging", "production"]
for env in environments:
    config_content = generate_config(env)
    await write_file(f"configs/{env}.json", config_content)
```

## Error Handling

### Security Errors
- **Path Outside Playground**: Attempts to write outside sandbox are rejected
- **Path Traversal**: `../` attempts to escape sandbox are blocked
- **Invalid Paths**: Malformed paths are validated and rejected

### File System Errors
- **Permission Denied**: Insufficient permissions for file operations
- **Disk Full**: No space available for file creation
- **Invalid Characters**: Unsupported characters in file names
- **Path Too Long**: File paths exceeding system limits

### Content Errors
- **Encoding Issues**: Character encoding problems
- **Large Content**: Content size limitations
- **Invalid Content**: Content that cannot be written

### Graceful Degradation
- **Partial Success**: Batch operations continue on individual failures
- **Detailed Reporting**: Specific error messages for each failure
- **Recovery Suggestions**: Helpful error messages with solutions
- **Status Tracking**: Clear success/failure indicators

## Best Practices

### File Organization
- **Logical Structure**: Organize files in meaningful directory hierarchies
- **Naming Conventions**: Use consistent, descriptive file names
- **Type Separation**: Group files by type (docs/, src/, tests/, etc.)
- **Version Control Ready**: Structure projects for version control systems

### Content Management
- **Encoding Consistency**: Use UTF-8 encoding for cross-platform compatibility
- **Line Endings**: Let the system handle line ending conversion
- **File Sizes**: Keep individual files reasonable in size
- **Content Validation**: Validate content before writing

### Security Considerations
- **Path Validation**: Always use relative paths when possible
- **Content Sanitization**: Validate content for security issues
- **Permission Checking**: Verify write permissions before operations
- **Audit Trail**: Monitor file creation and modification patterns

### Performance Optimization
- **Batch Operations**: Use `write_multiple_files` for multiple file operations
- **Directory Pre-creation**: Create directory structures before file writing
- **Content Preparation**: Prepare all content before starting write operations
- **Error Handling**: Handle errors gracefully to avoid partial states

## Limitations and Constraints

### Directory Restrictions
- **Sandbox Only**: Cannot write outside `C:\Users\usuario\agent_playground`
- **No System Directories**: Cannot access system or program directories
- **User Space Only**: Limited to user-accessible locations

### File Operations
- **Write Only**: Cannot modify existing files (only full rewrites)
- **No File Deletion**: Cannot delete files or directories
- **No File Moving**: Cannot move or rename files
- **Text Content Only**: Optimized for text files (binary via encoding)

### System Limitations
- **Disk Space**: Limited by available disk space
- **File Size**: Practical limits for individual file sizes
- **Path Length**: System-specific path length limitations
- **Permissions**: Requires write access to playground directory

## Troubleshooting

### Common Issues

**"Path must be within playground directory"**
- Ensure all paths resolve to within `C:\Users\usuario\agent_playground`
- Use relative paths instead of absolute paths outside playground
- Check for `../` patterns that might escape the sandbox

**"Permission denied"**
- Verify write permissions to the playground directory
- Check if antivirus software is blocking file operations
- Ensure the directory is not read-only

**"File already exists and overwrite is disabled"**
- Set `overwrite=True` in the write_file parameters
- Check if the file is currently open in another application
- Verify file permissions allow modification

**"Failed to create directory"**
- Check parent directory permissions
- Verify path length is within system limits
- Ensure directory name contains valid characters

### Performance Issues
- **Slow Write Operations**: Check disk space and system resources
- **Batch Operation Failures**: Reduce batch size or check individual file issues
- **Large File Problems**: Consider splitting large content into smaller files

## Future Enhancements

### Planned Features
- **File Editing**: Support for partial file modifications
- **File Management**: Move, rename, and delete operations
- **Binary File Support**: Native binary file handling
- **Template Engine**: Advanced project templating system
- **Version Control**: Git integration for project management
- **Compression**: Archive creation and extraction
- **File Monitoring**: Change detection and notification

### Integration Improvements
- **Cloud Storage**: Integration with Google Drive, Dropbox
- **Database Export**: Direct export to database formats
- **Code Generation**: Enhanced code generation capabilities
- **Documentation**: Automatic documentation generation