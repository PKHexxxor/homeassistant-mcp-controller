#!/bin/bash

# Dieses Skript erstellt die Grundstruktur für die Home Assistant MCP Integration Suite

# Hauptkomponentenverzeichnis
mkdir -p custom_components/mcp_integration

# Kernmodule
mkdir -p custom_components/mcp_integration/core
touch custom_components/mcp_integration/core/__init__.py
touch custom_components/mcp_integration/core/mcp_base.py
touch custom_components/mcp_integration/core/transport.py
touch custom_components/mcp_integration/core/tools.py

# Authentifizierungsmodule
mkdir -p custom_components/mcp_integration/auth
touch custom_components/mcp_integration/auth/__init__.py
touch custom_components/mcp_integration/auth/oauth2.py
touch custom_components/mcp_integration/auth/api_key.py
touch custom_components/mcp_integration/auth/session.py

# Server-Module
mkdir -p custom_components/mcp_integration/servers/ms365
mkdir -p custom_components/mcp_integration/servers/bookstack
mkdir -p custom_components/mcp_integration/servers/loki

# MS365 Server
touch custom_components/mcp_integration/servers/ms365/__init__.py
touch custom_components/mcp_integration/servers/ms365/server.py
touch custom_components/mcp_integration/servers/ms365/tools.py
touch custom_components/mcp_integration/servers/ms365/schema.py

# BookStack Server
touch custom_components/mcp_integration/servers/bookstack/__init__.py
touch custom_components/mcp_integration/servers/bookstack/server.py
touch custom_components/mcp_integration/servers/bookstack/tools.py
touch custom_components/mcp_integration/servers/bookstack/schema.py

# Loki Server
touch custom_components/mcp_integration/servers/loki/__init__.py
touch custom_components/mcp_integration/servers/loki/server.py
touch custom_components/mcp_integration/servers/loki/tools.py
touch custom_components/mcp_integration/servers/loki/schema.py

# Home Assistant Adapter
mkdir -p custom_components/mcp_integration/adapters
touch custom_components/mcp_integration/adapters/__init__.py
touch custom_components/mcp_integration/adapters/ms365.py
touch custom_components/mcp_integration/adapters/bookstack.py
touch custom_components/mcp_integration/adapters/loki.py

# Entity-Definitionen
mkdir -p custom_components/mcp_integration/entity
touch custom_components/mcp_integration/entity/__init__.py
touch custom_components/mcp_integration/entity/sensor.py
touch custom_components/mcp_integration/entity/binary_sensor.py

# Voice-Integration
mkdir -p custom_components/mcp_integration/voice
touch custom_components/mcp_integration/voice/__init__.py
touch custom_components/mcp_integration/voice/intents.py
touch custom_components/mcp_integration/voice/phrases.py

# Utility-Funktionen
mkdir -p custom_components/mcp_integration/utils
touch custom_components/mcp_integration/utils/__init__.py
touch custom_components/mcp_integration/utils/checkpointing.py
touch custom_components/mcp_integration/utils/logging.py

# Hauptkomponentendateien
touch custom_components/mcp_integration/__init__.py
touch custom_components/mcp_integration/manifest.json
touch custom_components/mcp_integration/const.py
touch custom_components/mcp_integration/config_flow.py
touch custom_components/mcp_integration/services.yaml
touch custom_components/mcp_integration/strings.json
touch custom_components/mcp_integration/intents.yaml

# Übersetzungen
mkdir -p custom_components/mcp_integration/translations
touch custom_components/mcp_integration/translations/en.json
touch custom_components/mcp_integration/translations/de.json

# Tests
mkdir -p tests/custom_components/mcp_integration
touch tests/custom_components/mcp_integration/__init__.py
touch tests/custom_components/mcp_integration/test_config_flow.py
touch tests/custom_components/mcp_integration/test_init.py
touch tests/custom_components/mcp_integration/conftest.py

# GitHub-Workflow-Dateien
mkdir -p .github/workflows
touch .github/workflows/ci.yml
touch .github/workflows/release.yml

echo "Projektstruktur für Home Assistant MCP Integration Suite erstellt."
