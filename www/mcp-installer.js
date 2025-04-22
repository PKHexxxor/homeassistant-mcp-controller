class MCPControllerInstaller extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <ha-card>
        <div class="card-content">
          <h2>MCP Controller installieren</h2>
          <p>Klicke auf den Button, um die MCP Controller Integration zu deiner Home Assistant-Installation hinzuzufügen.</p>
          <mwc-button raised id="install">Jetzt installieren</mwc-button>
          <p id="status"></p>
        </div>
        <style>
          ha-card {
            padding: 16px;
          }
          .card-content {
            display: flex;
            flex-direction: column;
            align-items: center;
          }
          mwc-button {
            margin-top: 16px;
            margin-bottom: 16px;
            background-color: var(--primary-color);
          }
        </style>
      </ha-card>
    `;
  }

  connectedCallback() {
    const button = this.shadowRoot.querySelector('#install');
    const status = this.shadowRoot.querySelector('#status');

    button.addEventListener('click', async () => {
      button.disabled = true;
      status.textContent = 'Installation wird vorbereitet...';

      try {
        // 1. Prüfen, ob HACS installiert ist
        const hacs = await this._checkHACS();
        if (!hacs) {
          status.textContent = 'HACS ist nicht installiert. Bitte installiere zuerst HACS.';
          button.disabled = false;
          return;
        }

        // 2. Repository zu HACS hinzufügen
        status.textContent = 'Füge Repository zu HACS hinzu...';
        await this._addRepository();

        // 3. Integration installieren
        status.textContent = 'Installiere MCP Controller...';
        await this._installIntegration();

        // 4. Home Assistant neu starten
        status.textContent = 'Starte Home Assistant neu...';
        await this._restartHomeAssistant();

        status.textContent = 'Installation abgeschlossen! Bitte gehe zu Einstellungen > Geräte & Dienste, um MCP Controller zu konfigurieren.';
      } catch (error) {
        console.error('Fehler bei der Installation:', error);
        status.textContent = `Fehler bei der Installation: ${error.message}. Bitte versuche die manuelle Installation.`;
        button.disabled = false;
      }
    });
  }

  async _checkHACS() {
    try {
      const hacsInfo = await this._callService('hacs', 'get_status', {});
      return !!hacsInfo;
    } catch (e) {
      return false;
    }
  }

  async _addRepository() {
    return this._callService('hacs', 'register_repository', {
      repository: 'PKHexxxor/homeassistant-mcp-controller',
      category: 'integration'
    });
  }

  async _installIntegration() {
    return this._callService('hacs', 'install', {
      repository: 'PKHexxxor/homeassistant-mcp-controller'
    });
  }

  async _restartHomeAssistant() {
    return this._callService('homeassistant', 'restart', {});
  }

  async _callService(domain, service, data) {
    return new Promise((resolve, reject) => {
      const eventId = new Date().toISOString();
      this._hass.connection.subscribeEvents((event) => {
        if (event.data.success) {
          resolve(event.data.result);
        } else {
          reject(new Error(event.data.error));
        }
      }, `${eventId}_result`);

      this._hass.callService(domain, service, data, eventId).catch(err => {
        reject(err);
      });
    });
  }

  set hass(hass) {
    this._hass = hass;
  }
}

customElements.define('mcp-controller-installer', MCPControllerInstaller);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'mcp-controller-installer',
  name: 'MCP Controller Installer',
  description: 'Eine Karte zum einfachen Installieren der MCP Controller Integration.'
});
