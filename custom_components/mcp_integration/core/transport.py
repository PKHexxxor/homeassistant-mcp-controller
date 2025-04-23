"""
Transport-Layer-Implementierungen für MCP-Server.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - asyncio
  - json
  - abc
  - logging
  - .mcp_base: MCPRequest, MCPResponse

TODO:
  - Implementierung weiterer Transport-Typen
  - Optimierung der Fehlerbehandlung
  - Timeout-Handling
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from .mcp_base import MCPRequest, MCPResponse

# Setup logging
_LOGGER = logging.getLogger(__name__)

class MCPTransport(ABC):
    """Abstrakte Basisklasse für MCP-Transport-Implementierungen."""
    
    def __init__(self):
        """Initialisiert den Transport-Layer."""
        self._request_handlers = {}
        self._connected = False
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def connect(self) -> bool:
        """Stellt die Verbindung her.
        
        Returns:
            True bei erfolgreicher Verbindung, False bei Fehler
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Trennt die Verbindung."""
        pass
        
    @abstractmethod
    async def send_response(self, response: MCPResponse) -> None:
        """Sendet eine Antwort über den Transport-Layer.
        
        Args:
            response: Die zu sendende Antwort
        """
        pass
        
    @abstractmethod
    async def receive_request(self) -> Optional[MCPRequest]:
        """Empfängt eine Anfrage über den Transport-Layer.
        
        Returns:
            Die empfangene Anfrage oder None bei Fehler
        """
        pass
        
    def register_request_handler(self, 
                               request_type: str, 
                               handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Registriert einen Handler für einen bestimmten Anfrage-Typ.
        
        Args:
            request_type: Typ der Anfrage
            handler: Handler-Funktion
        """
        self._request_handlers[request_type] = handler
        self._logger.debug(f"Handler für Anfrage-Typ '{request_type}' registriert")
        
    @property
    def is_connected(self) -> bool:
        """Gibt zurück, ob der Transport verbunden ist.
        
        Returns:
            True, wenn verbunden, sonst False
        """
        return self._connected

class StdioTransport(MCPTransport):
    """Transport-Layer, der Standard-Input/Output für die Kommunikation verwendet."""
    
    def __init__(self):
        """Initialisiert den Stdio-Transport."""
        super().__init__()
        self._reader = None
        self._writer = None
        
    async def connect(self) -> bool:
        """Stellt die Verbindung über Stdio her.
        
        Returns:
            True bei erfolgreicher Verbindung
        """
        self._reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(self._reader)
        self._writer = sys.stdout.buffer
        
        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin.buffer)
        
        self._connected = True
        self._logger.info("Stdio-Transport verbunden")
        return True
        
    async def disconnect(self) -> None:
        """Trennt die Stdio-Verbindung."""
        self._connected = False
        self._reader = None
        self._writer = None
        self._logger.info("Stdio-Transport getrennt")
        
    async def send_response(self, response: MCPResponse) -> None:
        """Sendet eine Antwort über Stdout.
        
        Args:
            response: Die zu sendende Antwort
        """
        if not self._connected:
            raise RuntimeError("Transport nicht verbunden")
            
        response_json = {
            "content": response.content,
        }
        
        if response.is_error:
            response_json["error"] = response.error
            
        if response.request_id:
            response_json["request_id"] = response.request_id
            
        json_data = json.dumps(response_json) + "\n"
        self._writer.write(json_data.encode("utf-8"))
        self._writer.flush()
        self._logger.debug(f"Antwort gesendet: {json_data[:100]}...")
        
    async def receive_request(self) -> Optional[MCPRequest]:
        """Empfängt eine Anfrage über Stdin.
        
        Returns:
            Die empfangene Anfrage oder None bei EOF
        """
        if not self._connected:
            raise RuntimeError("Transport nicht verbunden")
            
        try:
            line = await self._reader.readline()
            if not line:  # EOF
                return None
                
            data = json.loads(line.decode("utf-8"))
            
            if "tool" not in data:
                raise ValueError("Anfrage enthält kein 'tool'-Feld")
                
            request = MCPRequest(
                tool_name=data["tool"],
                params=data.get("params", {})
            )
            
            if "request_id" in data:
                request.request_id = data["request_id"]
                
            self._logger.debug(f"Anfrage empfangen: {line[:100]}...")
            return request
            
        except json.JSONDecodeError as e:
            self._logger.error(f"Fehler beim Dekodieren der JSON-Anfrage: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Fehler beim Empfangen der Anfrage: {e}")
            return None