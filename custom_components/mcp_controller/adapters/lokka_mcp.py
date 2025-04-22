"""Lokka MCP adapter specifically for Prinz-Thomas-GmbH/lokka server."""
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp

_LOGGER = logging.getLogger(__name__)

class LokkaMCPAdapter:
    """Adapter for interacting with Lokka (Loki) via MCP server."""
    
    def __init__(self, host: str, port: int):
        """Initialize the adapter.
        
        Args:
            host: The hostname where the Lokka MCP server is running
            port: The port number the Lokka MCP server is listening on
        """
        self.base_url = f"http://{host}:{port}/api"
        self.session = None
    
    async def async_setup(self):
        """Set up the adapter."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def async_close(self):
        """Close the adapter."""
        if self.session is not None:
            await self.session.close()
            self.session = None
    
    async def query_logs(self, query: str, start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None,
                       limit: int = 100) -> Dict[str, Any]:
        """Query logs from Lokka using the MCP server.
        
        Args:
            query: The LogQL query to execute
            start_time: The start time for the query range (defaults to 1 hour ago)
            end_time: The end time for the query range (defaults to now)
            limit: Maximum number of log lines to return
            
        Returns:
            Dictionary containing query results or error information
        """
        await self.async_setup()
        
        # Set default time range if not provided
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        
        # Convert to nanosecond timestamps
        start_ns = int(start_time.timestamp() * 1e9)
        end_ns = int(end_time.timestamp() * 1e9)
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "lokka",
            "tool_name": "query_logs",
            "arguments": {
                "query": query,
                "start": start_ns,
                "end": end_ns,
                "limit": limit
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Lokka MCP query failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error querying logs via Lokka MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def get_labels(self) -> Dict[str, Any]:
        """Get all label names from Lokka.
        
        Returns:
            Dictionary containing label names or error information
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "lokka",
            "tool_name": "get_labels",
            "arguments": {}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Lokka MCP get_labels failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error getting labels via Lokka MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def get_label_values(self, label: str) -> Dict[str, Any]:
        """Get all values for a specific label from Lokka.
        
        Args:
            label: The label name to get values for
            
        Returns:
            Dictionary containing label values or error information
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "lokka",
            "tool_name": "get_label_values",
            "arguments": {
                "label": label
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Lokka MCP get_label_values failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error getting label values via Lokka MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Check connection status to the Lokka MCP server.
        
        Returns:
            Dictionary with connection status information
        """
        await self.async_setup()
        
        try:
            # Try getting label names as a simple connectivity test
            result = await self.get_labels()
            
            if "error" not in result:
                return {"status": "online", "message": "Connected to Lokka MCP server"}
            else:
                return {"status": "error", "message": result["error"]}
                
        except Exception as ex:
            _LOGGER.error("Error connecting to Lokka MCP server: %s", str(ex))
            return {"status": "offline", "message": f"Connection failed: {str(ex)}"}