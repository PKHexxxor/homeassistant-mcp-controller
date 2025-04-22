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

## Ein-Klick-Installation

### Methode 1: Mit der Installations-Karte (am einfachsten)

1. Füge diese Karte zu deinem Dashboard hinzu:

```yaml
type: custom:mcp-controller-installer
```

2. Klicke auf den "Jetzt installieren"-Button und folge den Anweisungen

### Methode 2: HACS

1. Stelle sicher, dass [HACS](https://hacs.xyz/) installiert ist
2. Füge dieses Repository als benutzerdefiniertes Repository in HACS hinzu:
   - Gehe zu HACS > Integrationen > Drei-Punkte-Menü > Benutzerdefiniertes Repository
   - URL: `https://github.com/PKHexxxor/homeassistant-mcp-controller`
   - Kategorie: Integration
3. Suche nach "MCP Controller" in HACS und installiere es
4. Starte Home Assistant neu

### Manuelle Installation

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

## Installation der Widget-Karte

Um die Ein-Klick-Installationskarte zu nutzen:

1. Kopiere die Datei `/www/mcp-installer.js` in dein Home Assistant `/www/`-Verzeichnis
2. Füge die Ressource in deiner Lovelace-Konfiguration hinzu:
   ```yaml
   resources:
     - url: /local/mcp-installer.js
       type: module
   ```
3. Dann kannst du die Karte in jedem Dashboard verwenden:
   ```yaml
   type: custom:mcp-controller-installer
   ```

## Mitmachen

Beiträge sind willkommen! Erstelle gerne einen Pull Request.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die LICENSE-Datei für Details.