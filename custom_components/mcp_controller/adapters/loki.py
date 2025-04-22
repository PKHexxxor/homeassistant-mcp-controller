"""Loki MCP adapter."""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp

_LOGGER = logging.getLogger(__name__)

class LokiAdapter:
    """Adapter for interacting with Loki via MCP."""
    
    def __init__(self, host: str, port: int):
        """Initialize the adapter."""
        self.base_url = f"http://{host}:{port}"
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
    
    async def query_logs(self, query: str, time_range_minutes: int = 15) -> Dict[str, Any]:
        """Query logs from Loki."""
        await self.async_setup()
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_range_minutes)
        
        # Convert to Unix nanoseconds
        start_ns = int(start_time.timestamp() * 1e9)
        end_ns = int(end_time.timestamp() * 1e9)
        
        endpoint = "/loki/api/v1/query_range"
        params = {
            "query": query,
            "start": start_ns,
            "end": end_ns,
            "limit": 100,
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}{endpoint}", 
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Loki query failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error querying Loki: %s", str(ex))
            return {"error": str(ex)}
