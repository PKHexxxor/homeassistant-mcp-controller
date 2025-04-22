"""Bookstack MCP adapter specifically for PKHexxxor/mcp-bookstack server."""
import logging
import json
from typing import Any, Dict, List, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

class BookstackMCPAdapter:
    """Adapter for interacting with Bookstack via MCP server."""
    
    def __init__(self, host: str, port: int):
        """Initialize the adapter.
        
        Args:
            host: The hostname where the mcp-bookstack server is running
            port: The port number the mcp-bookstack server is listening on
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
    
    async def search_pages(self, query: str, page: int = 1, count: int = 10) -> Dict[str, Any]:
        """Search for pages in Bookstack using the MCP server.
        
        Args:
            query: The search term
            page: The page number of results to return
            count: The number of results per page (max 30)
            
        Returns:
            Dictionary containing search results or error information
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "bookstack",
            "tool_name": "search_pages",
            "arguments": {
                "query": query,
                "page": page,
                "count": count
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
                        "Bookstack MCP search failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error searching Bookstack via MCP: %s", str(ex))
            return {"error": str(ex)}
            
    async def get_connection_status(self) -> Dict[str, Any]:
        """Check connection status to the Bookstack MCP server.
        
        Returns:
            Dictionary with connection status information
        """
        await self.async_setup()
        
        try:
            # Simple request to verify the MCP server is responsive
            async with self.session.get(f"{self.base_url}/status") as response:
                if response.status == 200:
                    return {"status": "online", "message": "Connected to Bookstack MCP server"}
                else:
                    return {"status": "error", "message": f"Error {response.status}: {await response.text()}"}  
        except Exception as ex:
            _LOGGER.error("Error connecting to Bookstack MCP server: %s", str(ex))
            return {"status": "offline", "message": f"Connection failed: {str(ex)}"}
