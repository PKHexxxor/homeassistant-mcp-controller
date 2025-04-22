"""Config flow for MCP Controller integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_SERVICE_TYPE,
    CONF_NAME,
    SERVICE_TYPE_BOOKSTACK,
    SERVICE_TYPE_M365,
    SERVICE_TYPE_LOKI,
    DEFAULT_PORT_BOOKSTACK,
    DEFAULT_PORT_M365,
    DEFAULT_PORT_LOKI,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
)

_LOGGER = logging.getLogger(__name__)

class MCPControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MCP Controller."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return MCPControllerOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Define service type selection in first step
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_SERVICE_TYPE): vol.In(
                            [
                                SERVICE_TYPE_BOOKSTACK,
                                SERVICE_TYPE_M365,
                                SERVICE_TYPE_LOKI,
                            ]
                        ),
                    }
                ),
            )
        
        # Remember the selected service type
        self.service_type = user_input[CONF_SERVICE_TYPE]
        
        # Move to the service-specific configuration step
        return await self.async_step_service_config()

    async def async_step_service_config(self, user_input=None):
        """Handle service-specific configuration."""
        errors = {}

        if user_input is None:
            # Provide different schema based on service type
            if self.service_type == SERVICE_TYPE_BOOKSTACK:
                data_schema = vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=DEFAULT_PORT_BOOKSTACK): int,
                        vol.Required(CONF_API_KEY): str,
                        vol.Required(CONF_API_SECRET): str,
                    }
                )
            elif self.service_type == SERVICE_TYPE_M365:
                data_schema = vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                )
            elif self.service_type == SERVICE_TYPE_LOKI:
                data_schema = vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=DEFAULT_PORT_LOKI): int,
                    }
                )

            return self.async_show_form(
                step_id="service_config",
                data_schema=data_schema,
                errors=errors,
            )

        # TODO: Validate connection to the service

        # Combine with service type selection
        config_data = {**user_input, CONF_SERVICE_TYPE: self.service_type}
        
        # Create a unique ID based on the name and service type
        unique_id = f"{self.service_type}_{user_input[CONF_NAME]}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{self.service_type.capitalize()}: {user_input[CONF_NAME]}",
            data=config_data,
        )

class MCPControllerOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the MCP Controller."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Build options schema based on service type
        service_type = self.config_entry.data.get(CONF_SERVICE_TYPE)
        
        if service_type == SERVICE_TYPE_BOOKSTACK:
            options_schema = vol.Schema(
                {
                    vol.Optional(
                        CONF_HOST,
                        default=self.config_entry.data.get(CONF_HOST),
                    ): str,
                    vol.Optional(
                        CONF_PORT,
                        default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT_BOOKSTACK),
                    ): int,
                    vol.Optional(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY),
                    ): str,
                    vol.Optional(
                        CONF_API_SECRET,
                        default=self.config_entry.data.get(CONF_API_SECRET),
                    ): str,
                }
            )
        # Add other service types here...
        else:
            options_schema = vol.Schema({})

        return self.async_show_form(step_id="init", data_schema=options_schema)