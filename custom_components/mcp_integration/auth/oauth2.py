"""
OAuth2-Authentifizierungsimplementierung.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - datetime
  - logging
  - typing
  - requests
  - requests_oauthlib
  - homeassistant.helpers.config_entry_oauth2_flow
  - .session: AuthSession, SessionManager

TODO:
  - Integration mit Home Assistant OAuth2-Flow
  - Token-Erneuerungsmechanismus implementieren
  - Fehlerbehandlung verbessern
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import logging
import datetime
from typing import Dict, Any, Optional

from .session import AuthSession
from .__init__ import AuthProviderBase, register_auth_provider

# Setup logging
_LOGGER = logging.getLogger(__name__)

try:
    from homeassistant.helpers import config_entry_oauth2_flow
    from homeassistant.core import HomeAssistant
    HA_OAUTH2_AVAILABLE = True
except ImportError:
    HA_OAUTH2_AVAILABLE = False
    _LOGGER.warning("Home Assistant OAuth2-Modul nicht verfügbar")

class OAuth2Session(AuthSession):
    """Repräsentiert eine OAuth2-Authentifizierungssession."""
    
    def __init__(
        self,
        session_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
        scope: Optional[str] = None,
        token_type: str = "Bearer",
        metadata: Dict[str, Any] = None
    ):
        """Initialisiert eine neue OAuth2-Session.
        
        Args:
            session_id: Eindeutige ID der Session
            access_token: Access Token
            refresh_token: Refresh Token, falls vorhanden
            expires_at: Ablaufzeitpunkt des Access Tokens
            scope: Berechtigungsumfang
            token_type: Token-Typ (Bearer, etc.)
            metadata: Zusätzliche Metadaten
        """
        credentials = {
            "access_token": access_token,
            "token_type": token_type
        }
        
        if refresh_token:
            credentials["refresh_token"] = refresh_token
            
        if scope:
            credentials["scope"] = scope
            
        super().__init__(
            session_id=session_id,
            auth_type="oauth2",
            expires_at=expires_at,
            credentials=credentials,
            metadata=metadata or {}
        )
        
    @property
    def access_token(self) -> str:
        """Gibt das Access Token zurück."""
        return self.credentials.get("access_token", "")
        
    @property
    def refresh_token(self) -> Optional[str]:
        """Gibt das Refresh Token zurück."""
        return self.credentials.get("refresh_token")
        
    @property
    def token_type(self) -> str:
        """Gibt den Token-Typ zurück."""
        return self.credentials.get("token_type", "Bearer")
        
    @property
    def scope(self) -> Optional[str]:
        """Gibt den Berechtigungsumfang zurück."""
        return self.credentials.get("scope")
        
    def get_authorization_header(self) -> Dict[str, str]:
        """Gibt den Authorization-Header zurück.
        
        Returns:
            Authorization-Header als Dictionary
        """
        return {"Authorization": f"{self.token_type} {self.access_token}"}
        
    @classmethod
    def from_token_response(cls, session_id: str, token_data: Dict[str, Any]) -> 'OAuth2Session':
        """Erstellt eine OAuth2-Session aus einer Token-Antwort.
        
        Args:
            session_id: Eindeutige ID der Session
            token_data: Token-Daten
            
        Returns:
            OAuth2Session-Objekt
        """
        expires_at = None
        
        if "expires_in" in token_data:
            expires_in = token_data["expires_in"]
            expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        elif "expires_at" in token_data:
            expires_at = datetime.datetime.fromtimestamp(token_data["expires_at"])
            
        return cls(
            session_id=session_id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            scope=token_data.get("scope"),
            token_type=token_data.get("token_type", "Bearer")
        )

class OAuth2Provider(AuthProviderBase):
    """OAuth2-Authentifizierungsanbieter."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        scope: Optional[str] = None,
        redirect_uri: Optional[str] = None
    ):
        """Initialisiert den OAuth2-Provider.
        
        Args:
            client_id: Client ID
            client_secret: Client Secret
            authorize_url: URL für die Autorisierung
            token_url: URL für den Token-Austausch
            scope: Berechtigungsumfang
            redirect_uri: Redirect URI
        """
        super().__init__("oauth2")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.scope = scope
        self.redirect_uri = redirect_uri
        
    async def authenticate(self, **kwargs) -> OAuth2Session:
        """Führt die OAuth2-Authentifizierung durch.
        
        Args:
            **kwargs: Authentifizierungsparameter
            
        Returns:
            OAuth2Session-Objekt
            
        Raises:
            NotImplementedError: Diese Methode muss in Unterklassen implementiert werden
        """
        raise NotImplementedError("Diese Methode muss in Unterklassen implementiert werden")
        
    async def refresh_session(self, session: OAuth2Session) -> OAuth2Session:
        """Aktualisiert eine OAuth2-Session mit dem Refresh Token.
        
        Args:
            session: Die zu aktualisierende Session
            
        Returns:
            Aktualisierte Session
            
        Raises:
            ValueError: Wenn die Session kein Refresh Token enthält
        """
        if not session.refresh_token:
            raise ValueError("Session enthält kein Refresh Token")
            
        import requests
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": session.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Wenn refresh_token nicht in der Antwort enthalten ist, behalte das alte
            if "refresh_token" not in token_data and session.refresh_token:
                token_data["refresh_token"] = session.refresh_token
                
            # Erstelle neue Session mit den aktualisierten Token-Daten
            new_session = OAuth2Session.from_token_response(
                session_id=session.session_id,
                token_data=token_data
            )
            
            # Übernehme Metadaten
            new_session.metadata = session.metadata.copy()
            
            self._logger.info(f"OAuth2-Session aktualisiert: {session.session_id}")
            return new_session
            
        except Exception as e:
            self._logger.error(f"Fehler bei der Token-Aktualisierung: {e}")
            raise
        
    async def validate_session(self, session: AuthSession) -> bool:
        """Validiert eine OAuth2-Session.
        
        Args:
            session: Die zu validierende Session
            
        Returns:
            True, wenn die Session gültig ist, sonst False
        """
        if not isinstance(session, OAuth2Session):
            return False
            
        # Prüfe, ob die Session abgelaufen ist
        if session.is_expired():
            self._logger.debug(f"Session {session.session_id} ist abgelaufen")
            
            # Versuche, die Session zu aktualisieren, wenn ein Refresh Token vorhanden ist
            if session.refresh_token:
                try:
                    await self.refresh_session(session)
                    return True
                except Exception as e:
                    self._logger.error(f"Fehler bei der Session-Aktualisierung: {e}")
                    return False
            else:
                return False
                
        return True

# Registriere den OAuth2-Provider
register_auth_provider("oauth2", OAuth2Provider)

class HomeAssistantOAuth2Provider(OAuth2Provider):
    """OAuth2-Provider, der die Home Assistant-OAuth2-Implementierung verwendet."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        scope: Optional[str] = None,
        name: Optional[str] = None
    ):
        """Initialisiert den Home Assistant-OAuth2-Provider.
        
        Args:
            hass: Home Assistant-Instanz
            domain: Domain-Name
            client_id: Client ID
            client_secret: Client Secret
            authorize_url: URL für die Autorisierung
            token_url: URL für den Token-Austausch
            scope: Berechtigungsumfang
            name: Name des Providers
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=authorize_url,
            token_url=token_url,
            scope=scope
        )
        
        if not HA_OAUTH2_AVAILABLE:
            raise RuntimeError("Home Assistant OAuth2-Modul nicht verfügbar")
            
        self.hass = hass
        self.domain = domain
        self.name = name or domain
        
        # Erstelle OAuth2-Implementation
        self.oauth2_impl = config_entry_oauth2_flow.LocalOAuth2Implementation(
            hass,
            domain,
            client_id,
            client_secret,
            authorize_url,
            token_url,
            scope=scope
        )
        
    async def authenticate(self, **kwargs) -> OAuth2Session:
        """Führt die OAuth2-Authentifizierung mit Home Assistant durch.
        
        Args:
            **kwargs: Authentifizierungsparameter
            
        Returns:
            OAuth2Session-Objekt
            
        Raises:
            NotImplementedError: Diese Methode muss manuell im Home Assistant-Flow aufgerufen werden
        """
        raise NotImplementedError(
            "Die Authentifizierung muss über den Home Assistant-OAuth2-Flow durchgeführt werden"
        )
        
    async def get_authorize_url(self, state: str) -> str:
        """Gibt die Autorisierungs-URL zurück.
        
        Args:
            state: State-Parameter
            
        Returns:
            Autorisierungs-URL
        """
        return await self.oauth2_impl.async_get_authorize_url(state)
        
    async def handle_auth_callback(self, code: str) -> OAuth2Session:
        """Verarbeitet den OAuth2-Callback.
        
        Args:
            code: Autorisierungscode
            
        Returns:
            OAuth2Session-Objekt
        """
        import uuid
        
        token_data = await self.oauth2_impl.async_resolve_external_data(code)
        
        # Erstelle Session-ID
        session_id = str(uuid.uuid4())
        
        return OAuth2Session.from_token_response(
            session_id=session_id,
            token_data=token_data
        )

# Registriere den Home Assistant-OAuth2-Provider, wenn verfügbar
if HA_OAUTH2_AVAILABLE:
    register_auth_provider("ha_oauth2", HomeAssistantOAuth2Provider)