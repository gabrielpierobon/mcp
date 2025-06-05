#!/usr/bin/env python3
"""
Smart MCP Server Launcher
Automatically detects the best transport mode or allows explicit selection.

Usage:
  python run.py              # Auto-detect (stdio for Claude, HTTP for others)
  python run.py --http       # Force HTTP mode for n8n
  python run.py --stdio      # Force stdio mode for Claude Desktop
  python run.py --help       # Show help
"""

import sys
import os
import argparse

def detect_claude_desktop():
    """Detect if running from Claude Desktop environment."""
    # Claude Desktop typically sets specific environment variables
    claude_indicators = [
        "CLAUDE_DESKTOP",
        "ANTHROPIC_CLIENT"
    ]
    
    for indicator in claude_indicators:
        if os.getenv(indicator):
            return True
    
    # Check if running with no arguments and no explicit HTTP request
    if len(sys.argv) == 1 and not os.getenv("MCP_FORCE_HTTP"):
        # Check for TTY - Claude Desktop usually doesn't have one
        if not sys.stdin.isatty():
            return True
    
    return False

def show_help():
    """Show help information."""
    print("""
MCP Server Launcher

🤖 For Claude Desktop:
  python run.py              # Auto-detect mode
  python run.py --stdio      # Force stdio mode
  python run_claude.py       # Dedicated Claude launcher

🌐 For n8n Integration:
  python run.py --http       # Force HTTP mode  
  python run_http.py         # Dedicated n8n launcher

🔧 Environment Variables:
  MCP_SERVER_NAME            # Server name (default: auto)
  MCP_HOST                   # HTTP host (default: 0.0.0.0)
  MCP_PORT                   # HTTP port (default: 8000)
  MCP_FORCE_HTTP=1           # Force HTTP mode
  
  BRAVE_API_KEY              # Required for web search
  AIRTABLE_PERSONAL_ACCESS_TOKEN  # Required for Airtable
  GOOGLE_CREDENTIALS_FILE    # Optional for Google Workspace

📚 Documentation:
  docs/tools.md              # Complete tools documentation
  README.md                  # Setup and configuration guide
""")

def main():
    """Main launcher function."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="MCP Server Launcher",
        add_help=False  # We'll handle help ourselves
    )
    parser.add_argument("--http", action="store_true", help="Force HTTP mode for n8n")
    parser.add_argument("--stdio", action="store_true", help="Force stdio mode for Claude Desktop")
    parser.add_argument("--help", "-h", action="store_true", help="Show help")
    
    args, unknown = parser.parse_known_args()
    
    # Show help if requested
    if args.help:
        show_help()
        return
    
    # Determine the mode
    if args.http:
        print("🌐 Launching HTTP server for n8n integration...", file=sys.stderr)
        os.environ["MCP_FORCE_HTTP"] = "1"
        import run_http
        run_http.main()
        
    elif args.stdio:
        print("🤖 Launching stdio server for Claude Desktop...", file=sys.stderr)
        import run_claude
        run_claude.main()
        
    else:
        # Auto-detect mode
        if detect_claude_desktop() or os.getenv("MCP_FORCE_STDIO"):
            print("🤖 Auto-detected: Launching stdio server for Claude Desktop...", file=sys.stderr)
            import run_claude
            run_claude.main()
        else:
            print("🌐 Auto-detected: Launching HTTP server for external integration...", file=sys.stderr)
            print("💡 Use 'python run.py --stdio' to force Claude Desktop mode", file=sys.stderr)
            os.environ["MCP_FORCE_HTTP"] = "1"
            import run_http
            run_http.main()

if __name__ == "__main__":
    main()