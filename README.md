# Home Assistant MCP Controller

A Home Assistant integration to control various MCP (Media Control Protocol) servers including Bookstack, Microsoft 365, and Loki.

## Features

- Control and access Bookstack through MCP protocol
- Integrate with Microsoft 365 services
- Query Loki logs directly from Home Assistant
- Expandable design to add more MCP-compatible services

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS
3. Search for "MCP Controller" in HACS and install it
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/mcp_controller` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Home Assistant **Settings** → **Devices & Services**
2. Click **+ Add Integration** and search for "MCP Controller"
3. Select the service type you want to add (Bookstack, M365, or Loki)
4. Enter the required configuration information:
   - For Bookstack: hostname, port, API key, API secret
   - For Microsoft 365: client ID, client secret
   - For Loki: hostname, port

## Services

This integration provides the following services:

### Bookstack

- `mcp_controller.bookstack_search`: Search for content in Bookstack
- `mcp_controller.bookstack_create_page`: Create a new page in Bookstack

### Microsoft 365

- `mcp_controller.m365_list_emails`: List recent emails from Microsoft 365

### Loki

- `mcp_controller.loki_query_logs`: Query logs from Loki

## Voice Control with Home Assistant Assist

You can use the built-in Home Assistant Assist feature to control MCP services with voice commands. Add custom sentences to trigger automations that call MCP Controller services.

Example sentences:

- "Search Bookstack for home automation"
- "Show my recent emails"
- "Check system logs for errors"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.