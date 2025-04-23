"""
Core-Framework Initialisierung für die MCP Integration Suite.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - keine

TODO:
  - Konstanten für gemeinsame Core-Funktionalität definieren
  - Import-Helfer für Core-Module implementieren
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

# Exports für einfachere Importierung
from .mcp_base import AbstractMCPServer, MCPTool, MCPRequest, MCPResponse
from .transport import MCPTransport, StdioTransport
from .tools import ToolRegistry, register_tool

__all__ = [
    "AbstractMCPServer",
    "MCPTool",
    "MCPRequest",
    "MCPResponse",
    "MCPTransport",
    "StdioTransport",
    "ToolRegistry",
    "register_tool",
]
