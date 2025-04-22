"""Microsoft 365 MCP adapter."""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp

_LOGGER = logging.getLogger(__name__)

class M365Adapter:
    """Adapter for interacting with Microsoft 365 via MCP."""
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize the adapter."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = None
        self.token = None
    
    async def async_setup(self):
        """Set up the adapter."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self._ensure_token()
    
    async def async_close(self):
        """Close the adapter."""
        if self.session is not None:
            await self.session.close()
            self.session = None
    
    async def _ensure_token(self):
        """Ensure we have a valid token."""
        if self.token is None or self.token.get("expires_at", 0) < datetime.now().timestamp():
            # Token acquisition would normally use MSAL library
            # This is a simplified version for demonstration
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            }
            
            try:
                async with self.session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.token = {
                            "access_token": token_data["access_token"],
                            "expires_at": datetime.now().timestamp() + token_data["expires_in"]
                        }
                    else:
                        error_text = await response.text()
                        _LOGGER.error("Failed to get token: %s", error_text)
                        raise Exception(f"Failed to get token: {error_text}")
            except Exception as ex:
                _LOGGER.error("Error getting token: %s", str(ex))
                raise
    
    async def list_emails(self, folder: str = "inbox", count: int = 10) -> Dict[str, Any]:
        """List emails from a specific folder."""
        await self.async_setup()
        
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Content-Type": "application/json"
        }
        
        endpoint = f"/v1.0/me/mailFolders/{folder}/messages"
        params = {
            "$top": count,
            "$orderby": "receivedDateTime desc"
        }
        
        try:
            async with self.session.get(
                f"https://graph.microsoft.com{endpoint}", 
                headers=headers, 
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "M365 list emails failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error listing emails from M365: %s", str(ex))
            return {"error": str(ex)}
