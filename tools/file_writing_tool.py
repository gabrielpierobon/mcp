# tools/file_writing_tool.py
from typing import Dict, Any, Optional, List
import os
import json
from pathlib import Path
from datetime import datetime

# Define the allowed playground directory
PLAYGROUND_ROOT = Path("C:/Users/usuario/agent_playground")

def _ensure_playground_exists():
    """Ensure the playground directory exists."""
    PLAYGROUND_ROOT.mkdir(parents=True, exist_ok=True)
    return PLAYGROUND_ROOT

def _validate_playground_path(path_str: str) -> Path:
    """
    Validate that the path is within the allowed playground directory.
    Returns the validated absolute path or raises an exception.
    """
    # Ensure playground exists
    playground_root = _ensure_playground_exists()
    
    # Convert to Path object and resolve
    requested_path = Path(path_str)
    
    # If relative path, make it relative to playground
    if not requested_path.is_absolute():
        full_path = playground_root / requested_path
    else:
        full_path = requested_path
    
    # Resolve to absolute path
    full_path = full_path.resolve()
    
    # Ensure the path is within the playground
    try:
        full_path.relative_to(playground_root.resolve())
    except ValueError:
        raise ValueError(f"Path must be within the playground directory: {playground_root}")
    
    return full_path

async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_directories: bool = True,
    overwrite: bool = True
) -> Dict[str, Any]:
    """
    Write content to a file within the agent playground directory.
    
    Args:
        file_path: Path to the file to write (relative to playground or absolute within playground) (required)
        content: Content to write to the file (required)
        encoding: Text encoding to use (default: "utf-8")
        create_directories: Create parent directories if they don't exist (default: True)
        overwrite: Whether to overwrite existing files (default: True)
    
    Returns:
        Dictionary containing write operation results
    """
    print(f"INFO: write_file called with path: {file_path}")
    
    try:
        # Validate and get the full path within playground
        full_path = _validate_playground_path(file_path)
        
        # Check if file exists and overwrite policy
        if full_path.exists() and not overwrite:
            return {
                "error": f"File already exists and overwrite is disabled: {full_path.relative_to(PLAYGROUND_ROOT)}",
                "status": "error"
            }
        
        # Create parent directories if needed
        if create_directories:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        # Get file stats after writing
        stat = full_path.stat()
        
        return {
            "file_path": str(full_path.relative_to(PLAYGROUND_ROOT)),
            "absolute_path": str(full_path),
            "content_length": len(content),
            "size_bytes": stat.st_size,
            "encoding": encoding,
            "created_directories": create_directories,
            "overwritten": full_path.exists(),
            "modified_time": stat.st_mtime,
            "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "success"
        }
        
    except ValueError as e:
        # Path validation error
        return {
            "error": str(e),
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "error"
        }
    except PermissionError:
        return {
            "error": f"Permission denied writing to: {file_path}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: write_file failed: {str(e)}")
        return {
            "error": f"Failed to write file: {str(e)}",
            "status": "error"
        }

async def create_directory(
    directory_path: str
) -> Dict[str, Any]:
    """
    Create a directory within the agent playground.
    
    Args:
        directory_path: Path to the directory to create (relative to playground or absolute within playground) (required)
    
    Returns:
        Dictionary containing directory creation results
    """
    print(f"INFO: create_directory called with path: {directory_path}")
    
    try:
        # Validate and get the full path within playground
        full_path = _validate_playground_path(directory_path)
        
        # Create the directory (parents=True creates intermediate directories)
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "directory_path": str(full_path.relative_to(PLAYGROUND_ROOT)),
            "absolute_path": str(full_path),
            "created": True,
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "success"
        }
        
    except ValueError as e:
        # Path validation error
        return {
            "error": str(e),
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "error"
        }
    except PermissionError:
        return {
            "error": f"Permission denied creating directory: {directory_path}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: create_directory failed: {str(e)}")
        return {
            "error": f"Failed to create directory: {str(e)}",
            "status": "error"
        }

async def write_multiple_files(
    files: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Write multiple files in a single operation.
    
    Args:
        files: List of file dictionaries with 'path' and 'content' keys (required)
               Format: [{"path": "folder/file.txt", "content": "file content"}, ...]
    
    Returns:
        Dictionary containing results for each file write operation
    """
    print(f"INFO: write_multiple_files called with {len(files)} files")
    
    if not files:
        return {
            "error": "No files provided",
            "status": "error"
        }
    
    results = []
    successful_writes = 0
    failed_writes = 0
    
    for i, file_info in enumerate(files):
        if not isinstance(file_info, dict) or 'path' not in file_info or 'content' not in file_info:
            results.append({
                "index": i,
                "error": "File info must contain 'path' and 'content' keys",
                "status": "error"
            })
            failed_writes += 1
            continue
        
        # Write individual file
        result = await write_file(
            file_path=file_info['path'],
            content=file_info['content'],
            encoding=file_info.get('encoding', 'utf-8'),
            create_directories=file_info.get('create_directories', True),
            overwrite=file_info.get('overwrite', True)
        )
        
        result['index'] = i
        result['requested_path'] = file_info['path']
        results.append(result)
        
        if result.get('status') == 'success':
            successful_writes += 1
        else:
            failed_writes += 1
    
    return {
        "results": results,
        "total_files": len(files),
        "successful_writes": successful_writes,
        "failed_writes": failed_writes,
        "playground_root": str(PLAYGROUND_ROOT),
        "status": "success" if failed_writes == 0 else "partial" if successful_writes > 0 else "error"
    }

async def get_playground_info() -> Dict[str, Any]:
    """
    Get information about the agent playground directory.
    
    Returns:
        Dictionary containing playground directory information
    """
    print("INFO: get_playground_info called")
    
    try:
        playground_root = _ensure_playground_exists()
        
        # Get basic directory info
        stat = playground_root.stat()
        
        # Count files and directories
        total_files = 0
        total_dirs = 0
        
        for item in playground_root.rglob("*"):
            if item.is_file():
                total_files += 1
            elif item.is_dir():
                total_dirs += 1
        
        return {
            "playground_root": str(playground_root),
            "exists": playground_root.exists(),
            "is_directory": playground_root.is_dir(),
            "total_files": total_files,
            "total_directories": total_dirs,
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "created_time_readable": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified_time_readable": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "permissions": {
                "readable": os.access(playground_root, os.R_OK),
                "writable": os.access(playground_root, os.W_OK),
                "executable": os.access(playground_root, os.X_OK)
            },
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: get_playground_info failed: {str(e)}")
        return {
            "error": f"Failed to get playground info: {str(e)}",
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "error"
        }

async def create_project_structure(
    project_name: str,
    project_type: str = "general",
    files: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a complete project structure with common files and directories.
    
    Args:
        project_name: Name of the project (will be used as root directory name) (required)
        project_type: Type of project - "web", "python", "general", "react", "node" (default: "general")
        files: Optional dictionary of additional files to create {path: content} (optional)
    
    Returns:
        Dictionary containing project creation results
    """
    print(f"INFO: create_project_structure called with project: {project_name}, type: {project_type}")
    
    # Define project templates
    templates = {
        "web": {
            "directories": ["css", "js", "images", "assets"],
            "files": {
                "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Welcome to {project_name}</h1>
    <script src="js/script.js"></script>
</body>
</html>""",
                "css/style.css": """/* {project_name} Styles */
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f4f4f4;
}}

h1 {{
    color: #333;
    text-align: center;
}}""",
                "js/script.js": """// {project_name} JavaScript
console.log('Welcome to {project_name}!');

document.addEventListener('DOMContentLoaded', function() {{
    console.log('Page loaded successfully');
}});""",
                "README.md": """# {project_name}

A web project created with the MCP server.

## Structure
- `index.html` - Main HTML file
- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Image assets
"""
            }
        },
        "python": {
            "directories": ["src", "tests", "docs", "data"],
            "files": {
                "main.py": """#!/usr/bin/env python3
\"\"\"
{project_name} - Main application entry point
\"\"\"

def main():
    print("Welcome to {project_name}!")
    
if __name__ == "__main__":
    main()
""",
                "src/__init__.py": "# {project_name} package",
                "tests/test_main.py": """import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_example():
    assert True
""",
                "requirements.txt": """# {project_name} dependencies
requests
pytest
""",
                "README.md": """# {project_name}

A Python project created with the MCP server.

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Test
```bash
pytest tests/
```
"""
            }
        },
        "react": {
            "directories": ["src", "public", "src/components", "src/styles"],
            "files": {
                "package.json": """{
  "name": "{project_name_lower}",
  "version": "1.0.0",
  "description": "React project created with MCP server",
  "main": "src/index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}""",
                "public/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>""",
                "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
                "src/App.js": """import React from 'react';
import './styles/App.css';

function App() {
  return (
    <div className="App">
      <h1>Welcome to {project_name}</h1>
      <p>React project created with MCP server</p>
    </div>
  );
}

export default App;""",
                "src/styles/index.css": """body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}""",
                "src/styles/App.css": """.App {{
  text-align: center;
  padding: 20px;
}}

h1 {{
  color: #333;
}}""",
                "README.md": """# {project_name}

A React project created with the MCP server.

## Available Scripts

```bash
npm start    # Run development server
npm test     # Run tests
npm run build # Build for production
```
"""
            }
        },
        "general": {
            "directories": ["docs", "scripts", "data"],
            "files": {
                "README.md": """# {project_name}

Project created with the MCP server.

## Description
Add your project description here.

## Usage
Add usage instructions here.
""",
                "notes.txt": "Project notes for {project_name}\n\nAdd your notes here.",
                "scripts/setup.py": """#!/usr/bin/env python3
\"\"\"
Setup script for {project_name}
\"\"\"

print("Setting up {project_name}...")
"""
            }
        }
    }
    
    try:
        # Get the template
        if project_type not in templates:
            return {
                "error": f"Unknown project type: {project_type}. Available types: {list(templates.keys())}",
                "status": "error"
            }
        
        template = templates[project_type]
        project_root = project_name
        
        # Create project root directory
        root_result = await create_directory(project_root)
        if root_result.get("status") != "success":
            return root_result
        
        # Create directories
        created_dirs = []
        for directory in template.get("directories", []):
            dir_path = f"{project_root}/{directory}"
            dir_result = await create_directory(dir_path)
            if dir_result.get("status") == "success":
                created_dirs.append(dir_path)
        
        # Prepare files to create
        files_to_create = []
        
        # Add template files
        for file_path, content_template in template.get("files", {}).items():
            # Format the content with project name
            content = content_template.format(
                project_name=project_name,
                project_name_lower=project_name.lower()
            )
            files_to_create.append({
                "path": f"{project_root}/{file_path}",
                "content": content
            })
        
        # Add custom files
        if files:
            for file_path, content in files.items():
                files_to_create.append({
                    "path": f"{project_root}/{file_path}",
                    "content": content
                })
        
        # Write all files
        files_result = await write_multiple_files(files_to_create)
        
        return {
            "project_name": project_name,
            "project_type": project_type,
            "project_root": project_root,
            "created_directories": created_dirs,
            "files_created": files_result.get("successful_writes", 0),
            "files_failed": files_result.get("failed_writes", 0),
            "template_used": project_type,
            "playground_root": str(PLAYGROUND_ROOT),
            "status": "success" if files_result.get("failed_writes", 0) == 0 else "partial"
        }
        
    except Exception as e:
        print(f"ERROR: create_project_structure failed: {str(e)}")
        return {
            "error": f"Failed to create project structure: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the file writing tools with the MCP server"""
    mcp_instance.tool()(write_file)
    mcp_instance.tool()(create_directory)
    mcp_instance.tool()(write_multiple_files)
    mcp_instance.tool()(get_playground_info)
    mcp_instance.tool()(create_project_structure)
    print("INFO: File writing tools registered successfully")
    print(f"INFO: Playground directory: {PLAYGROUND_ROOT}")