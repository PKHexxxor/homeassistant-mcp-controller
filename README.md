# Home Assistant MCP Controller

Eine Home Assistant Integration zur Steuerung verschiedener MCP (Media Control Protocol) Server wie Bookstack, Microsoft 365 und Loki.

## Features

- Steuerung und Zugriff auf Bookstack über das MCP-Protokoll
- Integration mit Microsoft 365-Diensten
- Abfrage von Loki-Logs direkt aus Home Assistant
- Erweiterbare Architektur für weitere MCP-kompatible Dienste

## Speziell unterstützte MCP-Server

Diese Integration unterstützt speziell folgende MCP-Server:

1. [**PKHexxxor/mcp-bookstack**](https://github.com/PKHexxxor/mcp-bookstack) - MCP-Server für Bookstack
2. [**PKHexxxor/ms-365-mcp-server**](https://github.com/PKHexxxor/ms-365-mcp-server) - MCP-Server für Microsoft 365
3. [**Prinz-Thomas-GmbH/lokka**](https://github.com/Prinz-Thomas-GmbH/lokka) - MCP-Server für Loki Log-Abfragen

## Installation

### Methode 1: Ein-Klick-Installation (am einfachsten)

[![Ein-Klick-Installation](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=mcp_controller)

Klicke auf den Button oben und folge den Anweisungen, um die Integration zu installieren.

### Methode 2: HACS

1. Stelle sicher, dass [HACS](https://hacs.xyz/) installiert ist
2. Füge dieses Repository als benutzerdefiniertes Repository in HACS hinzu:
   - Gehe zu HACS > Integrationen > Drei-Punkte-Menü > Benutzerdefiniertes Repository
   - URL: `https://github.com/PKHexxxor/homeassistant-mcp-controller`
   - Kategorie: Integration
3. Suche nach "MCP Controller" in HACS und installiere es
4. Starte Home Assistant neu

### Methode 3: Manuelle Installation

1. Kopiere das `custom_components/mcp_controller`-Verzeichnis in dein Home Assistant `custom_components`-Verzeichnis
2. Starte Home Assistant neu

## Konfiguration

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen** und suche nach "MCP Controller"
3. Wähle den Dienst-Typ, den du hinzufügen möchtest:
   - **bookstack**: Standard Bookstack API
   - **m365**: Standard Microsoft 365 API
   - **loki**: Standard Loki API
   - **bookstack_mcp**: Bookstack über MCP-Server
   - **m365_mcp**: Microsoft 365 über MCP-Server
   - **lokka_mcp**: Loki über MCP-Server (Lokka)
4. Gib die erforderlichen Konfigurationsinformationen ein (je nach Service-Typ unterschiedlich)

## Services

Diese Integration stellt folgende Services bereit:

### Bookstack API

- `mcp_controller.bookstack_search`: Nach Inhalten in Bookstack suchen
- `mcp_controller.bookstack_create_page`: Eine neue Seite in Bookstack erstellen

### Microsoft 365 API

- `mcp_controller.m365_list_emails`: Aktuelle E-Mails von Microsoft 365 auflisten

### Loki API

- `mcp_controller.loki_query_logs`: Logs von Loki abfragen

### Bookstack MCP

- `mcp_controller.bookstack_mcp_search_pages`: Nach Seiten in Bookstack über den MCP-Server suchen

### Microsoft 365 MCP

- `mcp_controller.m365_mcp_login`: Bei Microsoft 365 über den MCP-Server anmelden
- `mcp_controller.m365_mcp_list_emails`: E-Mails von Microsoft 365 über den MCP-Server auflisten
- `mcp_controller.m365_mcp_list_calendar_events`: Kalendereinträge von Microsoft 365 über den MCP-Server auflisten

### Lokka MCP (Loki)

- `mcp_controller.lokka_mcp_query_logs`: Logs von Lokka über den MCP-Server abfragen
- `mcp_controller.lokka_mcp_get_labels`: Alle Label-Namen von Lokka über den MCP-Server abrufen
- `mcp_controller.lokka_mcp_get_label_values`: Alle Werte für ein bestimmtes Label von Lokka über den MCP-Server abrufen

## Sprachsteuerung mit Home Assistant Assist

Du kannst die eingebaute Home Assistant Assist-Funktion verwenden, um MCP-Dienste mit Sprachbefehlen zu steuern. Füge benutzerdefinierte Sätze hinzu, um Automatisierungen auszulösen, die MCP Controller-Dienste aufrufen.

Beispiel-Sätze:

- "Suche in Bookstack nach Home Automation"
- "Zeige meine aktuellen E-Mails"
- "Prüfe Systemlogs auf Fehler"

## Automatisierungsbeispiele

### Nach Bookstack-Seiten suchen

```yaml
alias: "Bookstack Suche - Anleitungen"
trigger:
  platform: state
  entity_id: input_text.bookstack_suche
action:
  - service: mcp_controller.bookstack_mcp_search_pages
    data:
      service_name: "Mein Bookstack"
      query: "{{ states('input_text.bookstack_suche') }}"
      count: 5
  - service: persistent_notification.create
    data:
      title: "Bookstack-Suchergebnisse"
      message: "{{ return }}"
```

### Microsoft 365 E-Mails abrufen

```yaml
alias: "E-Mail-Überprüfung"
trigger:
  platform: time_pattern
  minutes: "/30"
action:
  - service: mcp_controller.m365_mcp_list_emails
    data:
      service_name: "Mein Microsoft 365"
      count: 5
  - service: input_text.set_value
    data:
      entity_id: input_text.letzte_emails
      value: "{{ return.value | map(attribute='subject') | join('\n') }}"
```

### Logs nach Fehlern durchsuchen

```yaml
alias: "Log-Überwachung"
trigger:
  platform: time_pattern
  minutes: "/15"
action:
  - service: mcp_controller.lokka_mcp_query_logs
    data:
      service_name: "Mein Lokka Server"
      query: '{app="home-assistant"} |= "error"'
      limit: 20
  - condition: template
    value_template: "{{ return.streams | length > 0 }}"
  - service: notify.mobile_app
    data:
      title: "Log-Fehler gefunden!"
      message: "Es wurden {{ return.streams | length }} Log-Einträge mit Fehlern gefunden."
```

## Mitmachen

Beiträge sind willkommen! Erstelle gerne einen Pull Request.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die LICENSE-Datei für Details.