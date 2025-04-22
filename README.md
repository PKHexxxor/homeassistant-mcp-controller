# Home Assistant MCP Controller

Eine Home Assistant Integration zur Steuerung verschiedener MCP (Media Control Protocol) Server wie Bookstack, Microsoft 365 und Loki.

## Features

- Steuerung und Zugriff auf Bookstack über das MCP-Protokoll
- Integration mit Microsoft 365-Diensten
- Abfrage von Loki-Logs direkt aus Home Assistant
- Erweiterbare Architektur für weitere MCP-kompatible Dienste

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
3. Wähle den Dienst-Typ, den du hinzufügen möchtest (Bookstack, M365 oder Loki)
4. Gib die erforderlichen Konfigurationsinformationen ein:
   - Für Bookstack: Hostname, Port, API-Schlüssel, API-Secret
   - Für Microsoft 365: Client-ID, Client-Secret
   - Für Loki: Hostname, Port

## Services

Diese Integration stellt folgende Services bereit:

### Bookstack

- `mcp_controller.bookstack_search`: Nach Inhalten in Bookstack suchen
- `mcp_controller.bookstack_create_page`: Eine neue Seite in Bookstack erstellen

### Microsoft 365

- `mcp_controller.m365_list_emails`: Aktuelle E-Mails von Microsoft 365 auflisten

### Loki

- `mcp_controller.loki_query_logs`: Logs von Loki abfragen

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