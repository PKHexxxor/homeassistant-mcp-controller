"""OAuth API handler for Microsoft 365 authentication."""
import logging
import secrets
import time
from typing import Any, Callable, Dict, Optional, cast

import aiohttp
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.network import get_url
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Microsoft OAuth endpoints
MS_OAUTH_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MS_OAUTH_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
MS_GRAPH_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"

# OAuth scopes for Microsoft Graph API
MS_OAUTH_SCOPES = [
    "offline_access",            # Required for refresh token
    "User.Read",                 # Basic user profile
    "Mail.Read",                 # Read mail
    "Calendars.Read",            # Read calendar
    "Files.Read",                # Read OneDrive files
]


class M365OAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """Microsoft 365 OAuth2 implementation."""

    def __init__(
        self,
        hass: HomeAssistant,
        client_id: str,
        client_secret: str,
        name: str,
    ) -> None:
        """Initialize Microsoft 365 OAuth2 implementation."""
        self.name = name
        self.hass = hass
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = MS_OAUTH_TOKEN_URL
        self._scope = " ".join(MS_OAUTH_SCOPES)

        super().__init__(
            hass=hass,
            domain=DOMAIN,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=MS_OAUTH_AUTH_URL,
            token_url=MS_OAUTH_TOKEN_URL,
        )

    @property
    def extra_authorize_data(self) -> Dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": self._scope,
            "response_mode": "query",
            "response_type": "code",
        }

    async def async_resolve_external_data(self, external_data: Any) -> Dict[str, Any]:
        """Resolve the authorization code to tokens."""
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": external_data["code"],
                "redirect_uri": self.redirect_uri,
            }
        )

    async def _token_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a token request."""
        session = async_get_clientsession(self.hass)

        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret

        _LOGGER.debug("Token request data: %s", data)

        resp = await session.post(self._token_url, data=data)
        resp_json = await resp.json()

        if resp.status != 200:
            _LOGGER.error(
                "Token request failed: %s %s",
                resp.status,
                resp_json.get("error_description", resp_json.get("error", "")),
            )
            raise config_entry_oauth2_flow.OAuth2AuthImplementationError(
                f"Token request failed: {resp.status}"
            )

        return resp_json

    async def async_refresh_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh the token."""
        if "refresh_token" not in token:
            _LOGGER.warning("No refresh token available")
            raise config_entry_oauth2_flow.OAuth2AuthImplementationError(
                "No refresh token available"
            )

        return await self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            }
        )


class M365OAuthLoginView(HomeAssistantView):
    """Web view to initiate OAuth flow."""

    requires_auth = False
    url = "/api/mcp_controller/m365_oauth/{service_name}"
    name = "api:mcp_controller:m365_oauth"

    def __init__(
        self,
        oauth_implementations: Dict[str, M365OAuth2Implementation],
        login_callback: Callable[[HomeAssistant, str], None],
    ) -> None:
        """Initialize the OAuth login view."""
        self.oauth_implementations = oauth_implementations
        self.login_callback = login_callback

    async def get(self, request, service_name):
        """Handle GET requests for the view."""
        if service_name not in self.oauth_implementations:
            return self.json_message(f"Unknown service: {service_name}", 404)

        oauth_impl = self.oauth_implementations[service_name]
        
        # Generate a random state
        state = secrets.token_hex(16)
        
        # Store state with service name in flow manager
        request.app["hass"].data.setdefault(f"{DOMAIN}_oauth_states", {})[state] = service_name
        
        # Get the authorization URL
        authorize_url = await oauth_impl.async_get_authorize_url(state=state)
        
        # Return information about the authorization URL
        return self.json({
            "authorize_url": authorize_url,
            "service_name": service_name,
            "state": state,
        })


class M365OAuthCallbackView(HomeAssistantView):
    """Web view for OAuth callback handling."""

    requires_auth = False
    url = "/api/mcp_controller/m365_oauth_callback"
    name = "api:mcp_controller:m365_oauth_callback"

    def __init__(
        self,
        oauth_implementations: Dict[str, M365OAuth2Implementation],
        token_callback: Callable[[HomeAssistant, str, Dict[str, Any]], None],
    ) -> None:
        """Initialize the OAuth callback view."""
        self.oauth_implementations = oauth_implementations
        self.token_callback = token_callback

    async def get(self, request):
        """Handle GET requests for the view."""
        hass = request.app["hass"]
        
        # Get query parameters
        code = request.query.get("code")
        state = request.query.get("state")
        error = request.query.get("error")
        
        if error:
            error_description = request.query.get("error_description", "Unknown error")
            _LOGGER.error("OAuth error: %s - %s", error, error_description)
            return self.json_message(f"OAuth error: {error_description}", 400)
        
        if not code or not state:
            return self.json_message("Missing code or state parameter", 400)
        
        # Get service name from state
        oauth_states = hass.data.get(f"{DOMAIN}_oauth_states", {})
        service_name = oauth_states.pop(state, None)
        
        if not service_name:
            return self.json_message("Invalid state parameter", 400)
        
        # Get OAuth implementation
        if service_name not in self.oauth_implementations:
            return self.json_message(f"Unknown service: {service_name}", 404)
        
        oauth_impl = self.oauth_implementations[service_name]
        
        try:
            # Exchange code for token
            token_data = await oauth_impl.async_resolve_external_data({"code": code})
            
            # Call token callback
            if self.token_callback:
                self.token_callback(hass, service_name, token_data)
            
            # Return success HTML
            return aiohttp.web.Response(
                text="""
                <html>
                    <head><title>Login Successful</title></head>
                    <body>
                        <h1>Login Successful!</h1>
                        <p>You have successfully logged into Microsoft 365.</p>
                        <p>You can close this window now.</p>
                        <script>
                            window.onload = function() {
                                window.close();
                            };
                        </script>
                    </body>
                </html>
                """,
                content_type="text/html",
            )
        except Exception as ex:
            _LOGGER.exception("Error resolving external data: %s", ex)
            return self.json_message(f"Error obtaining token: {ex}", 500)


async def async_setup_oauth_api(
    hass: HomeAssistant,
    login_callback: Callable[[HomeAssistant, str], None],
    token_callback: Callable[[HomeAssistant, str, Dict[str, Any]], None],
) -> Dict[str, Any]:
    """Set up the OAuth API."""
    oauth_implementations = {}
    
    # Register views
    login_view = M365OAuthLoginView(oauth_implementations, login_callback)
    callback_view = M365OAuthCallbackView(oauth_implementations, token_callback)
    
    hass.http.register_view(login_view)
    hass.http.register_view(callback_view)
    
    return {
        "implementations": oauth_implementations,
        "login_view": login_view,
        "callback_view": callback_view,
    }


def register_oauth_implementation(
    hass: HomeAssistant,
    oauth_api: Dict[str, Any],
    service_name: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Register an OAuth implementation for a service."""
    implementations = oauth_api["implementations"]
    
    implementations[service_name] = M365OAuth2Implementation(
        hass=hass,
        client_id=client_id,
        client_secret=client_secret,
        name=service_name,
    )