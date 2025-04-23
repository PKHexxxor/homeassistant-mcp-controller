"""
Tool-Management und -Registrierung für MCP-Server.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - typing
  - logging
  - functools
  - .mcp_base: MCPTool

TODO:
  - Implementierung der Tool-Validierung
  - Erweiterung um dynamische Tool-Registrierung
  - Integration von Schema-Validierung
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import logging
import functools
from typing import Dict, Any, Callable, List, Optional, Type

from .mcp_base import MCPTool

# Setup logging
_LOGGER = logging.getLogger(__name__)

class ToolRegistry:
    """Zentrales Registry für MCP-Tools."""
    
    def __init__(self):
        """Initialisiert die Tool-Registry."""
        self._tools = {}  # Typ: Dict[str, MCPTool]
        self._logger = logging.getLogger(f"{__name__}.ToolRegistry")
        
    def register(self, tool: MCPTool) -> None:
        """Registriert ein Tool in der Registry.
        
        Args:
            tool: Das zu registrierende Tool
        
        Raises:
            ValueError: Wenn ein Tool mit demselben Namen bereits existiert
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool mit dem Namen '{tool.name}' ist bereits registriert")
            
        self._tools[tool.name] = tool
        self._logger.info(f"Tool '{tool.name}' registriert")
        
    def unregister(self, tool_name: str) -> None:
        """Entfernt ein Tool aus der Registry.
        
        Args:
            tool_name: Name des zu entfernenden Tools
            
        Raises:
            KeyError: Wenn kein Tool mit diesem Namen existiert
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool mit dem Namen '{tool_name}' ist nicht registriert")
            
        del self._tools[tool_name]
        self._logger.info(f"Tool '{tool_name}' entfernt")
        
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Gibt ein Tool anhand seines Namens zurück.
        
        Args:
            tool_name: Name des gesuchten Tools
            
        Returns:
            Das Tool oder None, wenn kein Tool mit diesem Namen existiert
        """
        return self._tools.get(tool_name)
        
    def get_all_tools(self) -> List[MCPTool]:
        """Gibt alle registrierten Tools zurück.
        
        Returns:
            Liste aller registrierten Tools
        """
        return list(self._tools.values())
        
    def get_tool_names(self) -> List[str]:
        """Gibt die Namen aller registrierten Tools zurück.
        
        Returns:
            Liste der Namen aller registrierten Tools
        """
        return list(self._tools.keys())
        
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Gibt die Schemas aller registrierten Tools zurück.
        
        Returns:
            Dictionary mit Tool-Namen als Schlüssel und Tool-Schemas als Werte
        """
        schemas = {}
        for name, tool in self._tools.items():
            schemas[name] = {
                "description": tool.description,
                "schema": tool.schema
            }
        return schemas
        
    def clear(self) -> None:
        """Entfernt alle Tools aus der Registry."""
        self._tools.clear()
        self._logger.info("Alle Tools wurden entfernt")

# Globale Tool-Registry
_REGISTRY = ToolRegistry()

def register_tool(tool_or_class: Type[MCPTool]) -> Type[MCPTool]:
    """Dekorator zur Registrierung eines Tools oder einer Tool-Klasse.
    
    Args:
        tool_or_class: Das Tool oder die Tool-Klasse
    
    Returns:
        Das unveränderte Tool oder die unveränderte Tool-Klasse
    
    Beispiel:
        @register_tool
        class MyTool(MCPTool):
            ...
    """
    if isinstance(tool_or_class, MCPTool):
        # Es ist eine Tool-Instanz
        _REGISTRY.register(tool_or_class)
        return tool_or_class
    
    # Es ist eine Tool-Klasse
    @functools.wraps(tool_or_class)
    def wrapper(*args, **kwargs):
        instance = tool_or_class(*args, **kwargs)
        _REGISTRY.register(instance)
        return instance
    
    return wrapper

def get_registry() -> ToolRegistry:
    """Gibt die globale Tool-Registry zurück.
    
    Returns:
        Die globale Tool-Registry
    """
    return _REGISTRY

def get_tool(tool_name: str) -> Optional[MCPTool]:
    """Gibt ein Tool anhand seines Namens zurück.
    
    Args:
        tool_name: Name des gesuchten Tools
        
    Returns:
        Das Tool oder None, wenn kein Tool mit diesem Namen existiert
    """
    return _REGISTRY.get_tool(tool_name)

def get_all_tools() -> List[MCPTool]:
    """Gibt alle registrierten Tools zurück.
    
    Returns:
        Liste aller registrierten Tools
    """
    return _REGISTRY.get_all_tools()