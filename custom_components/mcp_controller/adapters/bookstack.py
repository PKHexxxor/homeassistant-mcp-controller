"""Bookstack MCP adapter."""
import logging
import json
from typing import Any, Dict, List, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

class BookstackAdapter:
    """Adapter for interacting with Bookstack via MCP."""
    
    def __init__(self, host: str, port: int, api_key: str, api_secret: str):
        """Initialize the adapter."""
        self.base_url = f"http://{host}:{port}/api"
        self.api_key = api_key
        self.api_secret = api_secret
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
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search for content in Bookstack."""
        await self.async_setup()
        
        headers = {
            "Authorization": f"Token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
        }
        
        endpoint = "/search"
        params = {"query": query}
        
        try:
            async with self.session.get(
                f"{self.base_url}{endpoint}", 
                headers=headers, 
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Bookstack search failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error searching Bookstack: %s", str(ex))
            return {"error": str(ex)}
    
    async def create_page(self, book_id: int, title: str, content: str) -> Dict[str, Any]:
        """Create a new page in Bookstack."""
        await self.async_setup()
        
        headers = {
            "Authorization": f"Token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
        }
        
        endpoint = "/pages"
        data = {
            "book_id": book_id,
            "name": title,
            "markdown": content,
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}{endpoint}", 
                headers=headers, 
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Bookstack page creation failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error creating page in Bookstack: %s", str(ex))
            return {"error": str(ex)}
