"""Microsoft 365 MCP adapter specifically for PKHexxxor/ms-365-mcp-server."""
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp

_LOGGER = logging.getLogger(__name__)

class MS365MCPAdapter:
    """Adapter for interacting with Microsoft 365 via MCP server."""
    
    def __init__(self, host: str, port: int):
        """Initialize the adapter.
        
        Args:
            host: The hostname where the ms-365-mcp-server is running
            port: The port number the ms-365-mcp-server is listening on
        """
        self.base_url = f"http://{host}:{port}/api"
        self.session = None
        self.is_authenticated = False
    
    async def async_setup(self):
        """Set up the adapter."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        if not self.is_authenticated:
            await self.verify_login()
    
    async def async_close(self):
        """Close the adapter."""
        if self.session is not None:
            await self.session.close()
            self.session = None
    
    async def login(self, force: bool = False) -> Dict[str, Any]:
        """Login to Microsoft 365 using the MCP server.
        
        Args:
            force: Force a new login even if already logged in
            
        Returns:
            Dictionary containing login result or instructions
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "ms365",
            "tool_name": "login",
            "arguments": {
                "force": force
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if login was successful
                    if result.get("success"):
                        self.is_authenticated = True
                    
                    return result
                else:
                    _LOGGER.error(
                        "MS365 MCP login failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error logging in to MS365 via MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def verify_login(self) -> Dict[str, Any]:
        """Verify login status with Microsoft 365 MCP server.
        
        Returns:
            Dictionary containing login verification result
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "ms365",
            "tool_name": "verify-login",
            "arguments": {}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Update authentication status
                    self.is_authenticated = result.get("success", False)
                    
                    return result
                else:
                    _LOGGER.error(
                        "MS365 MCP verify-login failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error verifying login with MS365 MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def logout(self) -> Dict[str, Any]:
        """Logout from Microsoft 365 MCP server.
        
        Returns:
            Dictionary containing logout result
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        payload = {
            "server_name": "ms365",
            "tool_name": "logout",
            "arguments": {}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/use_mcp_tool", 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.is_authenticated = False
                    return result
                else:
                    _LOGGER.error(
                        "MS365 MCP logout failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error logging out from MS365 MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def list_mail_messages(self, expand: Optional[List[str]] = None, 
                              include_hidden_messages: Optional[str] = None,
                              orderby: Optional[List[str]] = None,
                              select: Optional[List[str]] = None) -> Dict[str, Any]:
        """List mail messages from Microsoft 365.
        
        Args:
            expand: Expand related entities
            include_hidden_messages: Include hidden messages
            orderby: Order items by property values
            select: Select properties to be returned
            
        Returns:
            Dictionary containing mail messages or error information
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        arguments = {}
        if expand is not None:
            arguments["expand"] = expand
        if include_hidden_messages is not None:
            arguments["includeHiddenMessages"] = include_hidden_messages
        if orderby is not None:
            arguments["orderby"] = orderby
        if select is not None:
            arguments["select"] = select
            
        payload = {
            "server_name": "ms365",
            "tool_name": "list-mail-messages",
            "arguments": arguments
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
                        "MS365 MCP list-mail-messages failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error listing mail messages via MS365 MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def list_calendar_events(self, expand: Optional[List[str]] = None,
                                orderby: Optional[List[str]] = None,
                                select: Optional[List[str]] = None) -> Dict[str, Any]:
        """List calendar events from Microsoft 365.
        
        Args:
            expand: Expand related entities
            orderby: Order items by property values
            select: Select properties to be returned
            
        Returns:
            Dictionary containing calendar events or error information
        """
        await self.async_setup()
        
        # Prepare the MCP request payload
        arguments = {}
        if expand is not None:
            arguments["expand"] = expand
        if orderby is not None:
            arguments["orderby"] = orderby
        if select is not None:
            arguments["select"] = select
            
        payload = {
            "server_name": "ms365",
            "tool_name": "list-calendar-events",
            "arguments": arguments
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
                        "MS365 MCP list-calendar-events failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return {"error": f"Failed with status {response.status}"}
        except Exception as ex:
            _LOGGER.error("Error listing calendar events via MS365 MCP: %s", str(ex))
            return {"error": str(ex)}
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Check connection status to the Microsoft 365 MCP server.
        
        Returns:
            Dictionary with connection status information
        """
        try:
            # Use verify_login to check connection status
            result = await self.verify_login()
            
            if result.get("success", False):
                return {
                    "status": "online", 
                    "message": "Connected to Microsoft 365 MCP server",
                    "user_info": result.get("userData", {})
                }
            else:
                return {
                    "status": "error", 
                    "message": "Authentication required",
                    "login_required": True
                }
                
        except Exception as ex:
            _LOGGER.error("Error connecting to Microsoft 365 MCP server: %s", str(ex))
            return {"status": "offline", "message": f"Connection failed: {str(ex)}"}