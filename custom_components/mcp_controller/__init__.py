"""The MCP Controller integration."""
import asyncio
import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, 
    PLATFORMS, 
    SERVICE_TYPE_BOOKSTACK,
    SERVICE_TYPE_M365,
    SERVICE_TYPE_LOKI,
    SERVICE_TYPE_BOOKSTACK_MCP,
    SERVICE_TYPE_M365_MCP,
    SERVICE_TYPE_LOKKA_MCP,
    CONF_SERVICE_TYPE,
    CONF_HOST,
    CONF_PORT,
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_NAME,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET
)
from .oauth_api import async_setup_oauth_api

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the MCP Controller component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Set up OAuth API for Microsoft 365
    oauth_api = await async_setup_oauth_api(
        hass=hass,
        login_callback=handle_oauth_login,
        token_callback=handle_oauth_token
    )
    
    # Store OAuth API in hass.data
    hass.data[DOMAIN]["oauth_api"] = oauth_api
    
    return True

def handle_oauth_login(hass: HomeAssistant, service_name: str) -> None:
    """Handle OAuth login callback."""
    _LOGGER.debug("OAuth login initiated for %s", service_name)

def handle_oauth_token(hass: HomeAssistant, service_name: str, token_data: dict) -> None:
    """Handle OAuth token callback."""
    _LOGGER.debug("OAuth token received for %s", service_name)
    
    # Find the adapter for this service and update its token
    for entry_id, service_data in hass.data.get(DOMAIN, {}).items():
        if isinstance(service_data, dict) and service_data.get("adapter_instance"):
            adapter = service_data.get("adapter_instance")
            if hasattr(adapter, "service_name") and adapter.service_name == service_name:
                _LOGGER.debug("Updating token for adapter %s", service_name)
                adapter.set_token(token_data)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MCP Controller from a config entry."""
    if DOMAIN not in hass.data:
        await async_setup(hass, {})
    
    # Store the entry data
    entry_data = dict(entry.data)
    hass.data[DOMAIN][entry.entry_id] = entry_data
    
    # Create service adapter instances
    service_type = entry_data.get(CONF_SERVICE_TYPE)
    
    if service_type == SERVICE_TYPE_M365:
        # For Microsoft 365, we'll create the OAuth-enabled adapter
        from .adapters.m365 import M365Adapter
        
        adapter = M365Adapter(
            hass=hass,
            client_id=entry_data.get(CONF_CLIENT_ID),
            client_secret=entry_data.get(CONF_CLIENT_SECRET),
            service_name=entry_data.get(CONF_NAME),
            oauth_api=hass.data[DOMAIN]["oauth_api"]
        )
        
        # Set up the adapter
        await adapter.async_setup()
        
        # Store the adapter instance for later use
        entry_data["adapter_instance"] = adapter
    
    # Register services
    await _register_services(hass)
    
    # Set up platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Close any active adapters
    entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
    adapter = entry_data.get("adapter_instance")
    if adapter and hasattr(adapter, "async_close"):
        await adapter.async_close()
    
    # Unload platforms
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, platform)
              for platform in PLATFORMS]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def _register_services(hass: HomeAssistant):
    """Register services for MCP Controller."""
    
    # Bookstack services
    async def bookstack_search(call: ServiceCall):
        """Search for content in Bookstack."""
        service_name = call.data.get("service_name")
        query = call.data.get("query")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_BOOKSTACK and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and perform search
                from .adapters.bookstack import BookstackAdapter
                adapter = BookstackAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT),
                    entry_data.get(CONF_API_KEY),
                    entry_data.get(CONF_API_SECRET)
                )
                try:
                    result = await adapter.search(query)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}

    async def bookstack_create_page(call: ServiceCall):
        """Create a new page in Bookstack."""
        service_name = call.data.get("service_name")
        book_id = call.data.get("book_id")
        title = call.data.get("title")
        content = call.data.get("content")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_BOOKSTACK and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and create page
                from .adapters.bookstack import BookstackAdapter
                adapter = BookstackAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT),
                    entry_data.get(CONF_API_KEY),
                    entry_data.get(CONF_API_SECRET)
                )
                try:
                    result = await adapter.create_page(book_id, title, content)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}

    # Microsoft 365 services with OAuth
    async def m365_login(call: ServiceCall):
        """Initiate OAuth login flow for Microsoft 365."""
        service_name = call.data.get("service_name")
        force = call.data.get("force", False)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365 and entry_data.get(CONF_NAME) == service_name:
                # Get the stored adapter instance
                adapter = entry_data.get("adapter_instance")
                if adapter:
                    try:
                        result = await adapter.async_login(force)
                        return result
                    except Exception as ex:
                        _LOGGER.error("Error initiating login: %s", ex)
                        return {"error": str(ex)}
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def m365_list_emails(call: ServiceCall):
        """List recent emails from Microsoft 365."""
        service_name = call.data.get("service_name")
        folder = call.data.get("folder", "inbox")
        count = call.data.get("count", 10)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365 and entry_data.get(CONF_NAME) == service_name:
                # Get the stored adapter instance
                adapter = entry_data.get("adapter_instance")
                if adapter:
                    try:
                        # Check if we're authenticated
                        if not adapter.is_token_valid():
                            return {"error": "Not authenticated. Please use m365_login service first."}
                        
                        result = await adapter.list_emails(folder, count)
                        return result
                    except Exception as ex:
                        _LOGGER.error("Error listing emails: %s", ex)
                        return {"error": str(ex)}
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def m365_list_calendar_events(call: ServiceCall):
        """List calendar events from Microsoft 365."""
        service_name = call.data.get("service_name")
        days = call.data.get("days", 7)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365 and entry_data.get(CONF_NAME) == service_name:
                # Get the stored adapter instance
                adapter = entry_data.get("adapter_instance")
                if adapter:
                    try:
                        # Check if we're authenticated
                        if not adapter.is_token_valid():
                            return {"error": "Not authenticated. Please use m365_login service first."}
                        
                        result = await adapter.list_calendar_events(days)
                        return result
                    except Exception as ex:
                        _LOGGER.error("Error listing calendar events: %s", ex)
                        return {"error": str(ex)}
        
        return {"error": f"Service {service_name} not found or not configured correctly"}

    # Loki services
    async def loki_query_logs(call: ServiceCall):
        """Query logs from Loki."""
        service_name = call.data.get("service_name")
        query = call.data.get("query")
        time_range = call.data.get("time_range", 15)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_LOKI and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and query logs
                from .adapters.loki import LokiAdapter
                adapter = LokiAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.query_logs(query, time_range_minutes=time_range)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}

    # Bookstack MCP services
    async def bookstack_mcp_search_pages(call: ServiceCall):
        """Search for pages in Bookstack through MCP server."""
        service_name = call.data.get("service_name")
        query = call.data.get("query")
        page = call.data.get("page", 1)
        count = call.data.get("count", 10)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_BOOKSTACK_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and search pages
                from .adapters.bookstack_mcp import BookstackMCPAdapter
                adapter = BookstackMCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.search_pages(query, page, count)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    # Microsoft 365 MCP services
    async def m365_mcp_login(call: ServiceCall):
        """Login to Microsoft 365 through MCP server."""
        service_name = call.data.get("service_name")
        force = call.data.get("force", False)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and login
                from .adapters.ms365_mcp import MS365MCPAdapter
                adapter = MS365MCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.login(force)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def m365_mcp_list_emails(call: ServiceCall):
        """List recent emails from Microsoft 365 through MCP server."""
        service_name = call.data.get("service_name")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and list emails
                from .adapters.ms365_mcp import MS365MCPAdapter
                adapter = MS365MCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.list_mail_messages()
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def m365_mcp_list_calendar_events(call: ServiceCall):
        """List calendar events from Microsoft 365 through MCP server."""
        service_name = call.data.get("service_name")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_M365_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and list calendar events
                from .adapters.ms365_mcp import MS365MCPAdapter
                adapter = MS365MCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.list_calendar_events()
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    # Lokka MCP services
    async def lokka_mcp_query_logs(call: ServiceCall):
        """Query logs from Lokka through MCP server."""
        service_name = call.data.get("service_name")
        query = call.data.get("query")
        limit = call.data.get("limit", 100)
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_LOKKA_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and query logs
                from .adapters.lokka_mcp import LokkaMCPAdapter
                adapter = LokkaMCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    # Calculate default time range (last hour)
                    end_time = datetime.now()
                    start_time = end_time - timedelta(hours=1)
                    
                    result = await adapter.query_logs(query, start_time, end_time, limit)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def lokka_mcp_get_labels(call: ServiceCall):
        """Get all label names from Lokka through MCP server."""
        service_name = call.data.get("service_name")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_LOKKA_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and get labels
                from .adapters.lokka_mcp import LokkaMCPAdapter
                adapter = LokkaMCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.get_labels()
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    async def lokka_mcp_get_label_values(call: ServiceCall):
        """Get all values for a specific label from Lokka through MCP server."""
        service_name = call.data.get("service_name")
        label = call.data.get("label")
        
        # Find the entry that matches the service name
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and entry_data.get(CONF_SERVICE_TYPE) == SERVICE_TYPE_LOKKA_MCP and entry_data.get(CONF_NAME) == service_name:
                # Create adapter and get label values
                from .adapters.lokka_mcp import LokkaMCPAdapter
                adapter = LokkaMCPAdapter(
                    entry_data.get(CONF_HOST),
                    entry_data.get(CONF_PORT)
                )
                try:
                    result = await adapter.get_label_values(label)
                    return result
                finally:
                    await adapter.async_close()
        
        return {"error": f"Service {service_name} not found or not configured correctly"}
    
    # Register all services
    hass.services.async_register(DOMAIN, "bookstack_search", bookstack_search)
    hass.services.async_register(DOMAIN, "bookstack_create_page", bookstack_create_page)
    hass.services.async_register(DOMAIN, "m365_login", m365_login)  # New OAuth login service
    hass.services.async_register(DOMAIN, "m365_list_emails", m365_list_emails)
    hass.services.async_register(DOMAIN, "m365_list_calendar_events", m365_list_calendar_events)  # New calendar service
    hass.services.async_register(DOMAIN, "loki_query_logs", loki_query_logs)
    hass.services.async_register(DOMAIN, "bookstack_mcp_search_pages", bookstack_mcp_search_pages)
    hass.services.async_register(DOMAIN, "m365_mcp_login", m365_mcp_login)
    hass.services.async_register(DOMAIN, "m365_mcp_list_emails", m365_mcp_list_emails)
    hass.services.async_register(DOMAIN, "m365_mcp_list_calendar_events", m365_mcp_list_calendar_events)
    hass.services.async_register(DOMAIN, "lokka_mcp_query_logs", lokka_mcp_query_logs)
    hass.services.async_register(DOMAIN, "lokka_mcp_get_labels", lokka_mcp_get_labels)
    hass.services.async_register(DOMAIN, "lokka_mcp_get_label_values", lokka_mcp_get_label_values)