"""Microsoft 365 MCP adapter."""
import logging
import webbrowser
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..oauth_api import register_oauth_implementation

_LOGGER = logging.getLogger(__name__)

class M365Adapter:
    """Adapter for interacting with Microsoft 365 via Graph API with OAuth."""
    
    def __init__(
        self, 
        hass: HomeAssistant,
        client_id: str, 
        client_secret: str,
        service_name: str,
        oauth_api: Dict[str, Any]
    ):
        """Initialize the adapter."""
        self.hass = hass
        self.client_id = client_id
        self.client_secret = client_secret
        self.service_name = service_name
        self.oauth_api = oauth_api
        self.session = None
        self.token = None
        self.token_expiry = None
        self.user_info = None
        
        # Register OAuth implementation
        register_oauth_implementation(
            hass=hass,
            oauth_api=oauth_api,
            service_name=service_name,
            client_id=client_id,
            client_secret=client_secret,
        )
    
    async def async_setup(self):
        """Set up the adapter."""
        if self.session is None:
            self.session = async_get_clientsession(self.hass)
    
    async def async_close(self):
        """Close the adapter."""
        # We don't close the session as it's provided by HA
        self.session = None
    
    def is_token_valid(self) -> bool:
        """Check if the token is valid."""
        if not self.token:
            return False
        
        if not self.token_expiry:
            return False
            
        # Consider token expired 5 minutes before actual expiry
        return datetime.now() < (self.token_expiry - timedelta(minutes=5))
    
    async def get_authorize_url(self) -> str:
        """Get the authorization URL for OAuth login."""
        oauth_impl = self.oauth_api["implementations"].get(self.service_name)
        if not oauth_impl:
            raise Exception(f"No OAuth implementation registered for {self.service_name}")
        
        # Call the login view to get the authorization URL
        login_url = f"/api/mcp_controller/m365_oauth/{self.service_name}"
        
        # Use the session to make a request to our own API
        full_url = f"{self.hass.config.api.base_url}{login_url}"
        
        async with self.session.get(full_url) as response:
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error("Failed to get authorization URL: %s", error_text)
                raise Exception(f"Failed to get authorization URL: {error_text}")
            
            result = await response.json()
            return result["authorize_url"]
    
    def open_auth_page(self, auth_url: str) -> bool:
        """Open the authorization page in a browser."""
        try:
            webbrowser.open(auth_url)
            return True
        except Exception as ex:
            _LOGGER.error("Failed to open browser: %s", ex)
            return False
    
    def set_token(self, token_data: Dict[str, Any]) -> None:
        """Set the token data from OAuth callback."""
        self.token = token_data
        
        # Calculate expiry time
        if "expires_in" in token_data:
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
        else:
            # Default to 1 hour if not specified
            self.token_expiry = datetime.now() + timedelta(hours=1)
            
        _LOGGER.debug(
            "Token set for %s, expires at %s", 
            self.service_name, 
            self.token_expiry.isoformat()
        )
    
    async def async_login(self, force: bool = False) -> Dict[str, Any]:
        """Initiate the OAuth login flow."""
        await self.async_setup()
        
        if not force and self.is_token_valid():
            return {"status": "already_logged_in", "user_info": self.user_info}
        
        try:
            auth_url = await self.get_authorize_url()
            browser_opened = self.open_auth_page(auth_url)
            
            return {
                "status": "auth_initiated",
                "auth_url": auth_url,
                "browser_opened": browser_opened,
                "message": "Authorization initiated. Please complete login in your browser."
            }
        except Exception as ex:
            _LOGGER.error("Error initiating login: %s", ex)
            return {"status": "error", "error": str(ex)}
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get user information from Microsoft Graph API."""
        if not self.is_token_valid():
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.get(
                "https://graph.microsoft.com/v1.0/me", 
                headers=headers
            ) as response:
                if response.status == 200:
                    self.user_info = await response.json()
                    return self.user_info
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "Failed to get user info: %s - %s", 
                        response.status, 
                        error_text
                    )
                    return {"error": f"Failed with status {response.status}: {error_text}"}
        except Exception as ex:
            _LOGGER.error("Error getting user info: %s", ex)
            return {"error": str(ex)}
    
    async def list_emails(self, folder: str = "inbox", count: int = 10) -> Dict[str, Any]:
        """List emails from a specific folder."""
        if not self.is_token_valid():
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Content-Type": "application/json"
        }
        
        endpoint = f"/v1.0/me/mailFolders/{folder}/messages"
        params = {
            "$top": count,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,importance"
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
                    error_text = await response.text()
                    _LOGGER.error(
                        "M365 list emails failed with status %s: %s", 
                        response.status, 
                        error_text
                    )
                    return {"error": f"Failed with status {response.status}: {error_text}"}
        except Exception as ex:
            _LOGGER.error("Error listing emails from M365: %s", ex)
            return {"error": str(ex)}
    
    async def list_calendar_events(self, days: int = 7) -> Dict[str, Any]:
        """List calendar events for the next X days."""
        if not self.is_token_valid():
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Content-Type": "application/json",
            "Prefer": "outlook.timezone=\"UTC\""
        }
        
        # Calculate time window
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        # Format dates for Microsoft Graph
        start_datetime = now.isoformat() + "Z"
        end_datetime = end_date.isoformat() + "Z"
        
        endpoint = "/v1.0/me/calendarView"
        params = {
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "$select": "id,subject,organizer,start,end,location,bodyPreview",
            "$orderby": "start/dateTime",
            "$top": 50
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
                    error_text = await response.text()
                    _LOGGER.error(
                        "M365 list calendar events failed with status %s: %s", 
                        response.status, 
                        error_text
                    )
                    return {"error": f"Failed with status {response.status}: {error_text}"}
        except Exception as ex:
            _LOGGER.error("Error listing calendar events from M365: %s", ex)
            return {"error": str(ex)}