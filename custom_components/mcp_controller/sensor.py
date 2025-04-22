"""Sensor platform for MCP Controller integration."""
import logging
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, 
    CONF_SERVICE_TYPE, 
    CONF_NAME, 
    SERVICE_TYPE_BOOKSTACK, 
    SERVICE_TYPE_M365, 
    SERVICE_TYPE_LOKI,
    SERVICE_TYPE_BOOKSTACK_MCP,
    SERVICE_TYPE_M365_MCP,
    SERVICE_TYPE_LOKKA_MCP
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up MCP Controller sensors based on a config entry."""
    config = entry.data
    service_type = config.get(CONF_SERVICE_TYPE)
    name = config.get(CONF_NAME)
    
    entities = []
    
    if service_type == SERVICE_TYPE_BOOKSTACK:
        entities.append(BookstackStatusSensor(name, config))
    elif service_type == SERVICE_TYPE_M365:
        entities.append(M365StatusSensor(name, config))
    elif service_type == SERVICE_TYPE_LOKI:
        entities.append(LokiStatusSensor(name, config))
    elif service_type == SERVICE_TYPE_BOOKSTACK_MCP:
        entities.append(BookstackMCPStatusSensor(name, config))
    elif service_type == SERVICE_TYPE_M365_MCP:
        entities.append(MS365MCPStatusSensor(name, config))
    elif service_type == SERVICE_TYPE_LOKKA_MCP:
        entities.append(LokkaMCPStatusSensor(name, config))
    
    if entities:
        async_add_entities(entities)

class MCPControllerSensor(SensorEntity):
    """Base class for MCP Controller sensors."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        self._name = name
        self._config = config
        self._attr_state = "unknown"
        self._attr_available = False
    
    @property
    def name(self):
        """Return the name of the entity."""
        return self._name
    
    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self._config.get(CONF_SERVICE_TYPE)}_{self._name}"
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr_state

class BookstackStatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Bookstack connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:book-open-page-variant"
        
    async def async_update(self):
        """Update the sensor state."""
        # TODO: Implement actual connection check to Bookstack
        self._attr_state = "online"
        self._attr_available = True

class M365StatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Microsoft 365 connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:microsoft"
        
    async def async_update(self):
        """Update the sensor state."""
        # TODO: Implement actual connection check to M365
        self._attr_state = "online"
        self._attr_available = True

class LokiStatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Loki connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:text-search"
        
    async def async_update(self):
        """Update the sensor state."""
        # TODO: Implement actual connection check to Loki
        self._attr_state = "online"
        self._attr_available = True

class BookstackMCPStatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Bookstack MCP server connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:book-open-page-variant"
        self._host = config.get("host")
        self._port = config.get("port")
        self._extra_attributes = {}
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return self._extra_attributes
        
    async def async_update(self):
        """Update the sensor state."""
        from .adapters.bookstack_mcp import BookstackMCPAdapter
        
        adapter = BookstackMCPAdapter(self._host, self._port)
        try:
            status = await adapter.get_connection_status()
            self._attr_state = status.get("status", "unknown")
            self._extra_attributes = {"message": status.get("message", "")}
            self._attr_available = self._attr_state == "online"
        except Exception as ex:
            _LOGGER.error("Error checking Bookstack MCP status: %s", str(ex))
            self._attr_state = "error"
            self._extra_attributes = {"error": str(ex)}
            self._attr_available = False
        finally:
            await adapter.async_close()

class MS365MCPStatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Microsoft 365 MCP server connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:microsoft"
        self._host = config.get("host")
        self._port = config.get("port")
        self._extra_attributes = {}
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return self._extra_attributes
        
    async def async_update(self):
        """Update the sensor state."""
        from .adapters.ms365_mcp import MS365MCPAdapter
        
        adapter = MS365MCPAdapter(self._host, self._port)
        try:
            status = await adapter.get_connection_status()
            self._attr_state = status.get("status", "unknown")
            
            # Add attributes based on status
            attributes = {"message": status.get("message", "")}
            
            # If we have user info, add it
            if "user_info" in status:
                user_info = status.get("user_info", {})
                attributes["user_name"] = user_info.get("displayName", "")
                attributes["user_email"] = user_info.get("userPrincipalName", "")
                
            # If login is required, indicate that
            if status.get("login_required", False):
                attributes["login_required"] = True
                
            self._extra_attributes = attributes
            self._attr_available = self._attr_state in ["online", "error"]
        except Exception as ex:
            _LOGGER.error("Error checking Microsoft 365 MCP status: %s", str(ex))
            self._attr_state = "error"
            self._extra_attributes = {"error": str(ex)}
            self._attr_available = False
        finally:
            await adapter.async_close()

class LokkaMCPStatusSensor(MCPControllerSensor):
    """Sensor that shows the status of the Lokka MCP server connection."""
    
    def __init__(self, name, config):
        """Initialize the sensor."""
        super().__init__(f"{name} Status", config)
        self._attr_icon = "mdi:text-search"
        self._host = config.get("host")
        self._port = config.get("port")
        self._extra_attributes = {}
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return self._extra_attributes
        
    async def async_update(self):
        """Update the sensor state."""
        from .adapters.lokka_mcp import LokkaMCPAdapter
        
        adapter = LokkaMCPAdapter(self._host, self._port)
        try:
            status = await adapter.get_connection_status()
            self._attr_state = status.get("status", "unknown")
            self._extra_attributes = {"message": status.get("message", "")}
            self._attr_available = self._attr_state == "online"
        except Exception as ex:
            _LOGGER.error("Error checking Lokka MCP status: %s", str(ex))
            self._attr_state = "error"
            self._extra_attributes = {"error": str(ex)}
            self._attr_available = False
        finally:
            await adapter.async_close()