#!/usr/bin/env python3
"""Entrypoint for the Noetrix ATS Model Context Protocol (MCP) Server.

Usage:
  python mcp_server.py

For Claude Desktop (claude_desktop_config.json) or Cursor (.cursor/mcp.json):
{
  "mcpServers": {
    "noetrix-ats": {
      "command": "python",
      "args": ["C:\\path\\to\\Noetrix\\noetrix\\backend\\mcp_server.py"]
    }
  }
}
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.mcp_server import main

if __name__ == "__main__":
    main()
