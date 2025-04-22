"""Constants for the MCP Controller integration."""

DOMAIN = "mcp_controller"

# List of platforms that this integration supports
PLATFORMS = ["sensor"]

# Service types
SERVICE_TYPE_BOOKSTACK = "bookstack"
SERVICE_TYPE_M365 = "m365"
SERVICE_TYPE_LOKI = "loki"
SERVICE_TYPE_BOOKSTACK_MCP = "bookstack_mcp"
SERVICE_TYPE_M365_MCP = "m365_mcp"
SERVICE_TYPE_LOKKA_MCP = "lokka_mcp"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_SERVICE_TYPE = "service_type"
CONF_NAME = "name"

# Default values
DEFAULT_PORT_BOOKSTACK = 80
DEFAULT_PORT_M365 = 443
DEFAULT_PORT_LOKI = 3100
DEFAULT_PORT_BOOKSTACK_MCP = 3000
DEFAULT_PORT_M365_MCP = 3001
DEFAULT_PORT_LOKKA_MCP = 3002