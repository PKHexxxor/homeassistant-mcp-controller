"""Sensor platform for MCP Controller integration."""
import logging
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_SERVICE_TYPE, CONF_NAME, SERVICE_TYPE_BOOKSTACK, SERVICE_TYPE_M365, SERVICE_TYPE_LOKI

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