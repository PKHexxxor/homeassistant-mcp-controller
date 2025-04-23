"""
API-Key-Authentifizierungsimplementierung.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - datetime
  - logging
  - typing
  - .session: AuthSession
  - .__init__: AuthProviderBase, register_auth_provider

TODO:
  - Sichere Speicherung der API-Keys implementieren
  - Validierungsmechanismen für API-Keys erweitern
  - Integration mit Home Assistant-Secrets
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import logging
import datetime
import hashlib
from typing import Dict, Any, Optional, Tuple

from .session import AuthSession
from .__init__ import AuthProviderBase, register_auth_provider

# Setup logging
_LOGGER = logging.getLogger(__name__)

class APIKeySession(AuthSession):
    """Repräsentiert eine API-Key-Authentifizierungssession."""
    
    def __init__(
        self,
        session_id: str,
        api_key: str,
        api_secret: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
        key_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Initialisiert eine neue API-Key-Session.
        
        Args:
            session_id: Eindeutige ID der Session
            api_key: API-Key
            api_secret: API-Secret, falls vorhanden
            expires_at: Ablaufzeitpunkt der Session
            key_id: ID des API-Keys
            metadata: Zusätzliche Metadaten
        """
        credentials = {
            "api_key": api_key
        }
        
        if api_secret:
            # Speichere eine Hash-Version des Secrets für Validierungszwecke
            credentials["api_secret_hash"] = self._hash_secret(api_secret)
            # Speichere das eigentliche Secret nur, wenn es für die API benötigt wird
            credentials["api_secret"] = api_secret
            
        if key_id:
            credentials["key_id"] = key_id
            
        super().__init__(
            session_id=session_id,
            auth_type="api_key",
            expires_at=expires_at,
            credentials=credentials,
            metadata=metadata or {}
        )
        
    @property
    def api_key(self) -> str:
        """Gibt den API-Key zurück."""
        return self.credentials.get("api_key", "")
        
    @property
    def api_secret(self) -> Optional[str]:
        """Gibt das API-Secret zurück."""
        return self.credentials.get("api_secret")
        
    @property
    def key_id(self) -> Optional[str]:
        """Gibt die Key-ID zurück."""
        return self.credentials.get("key_id")
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Gibt die Authentifizierungs-Header zurück.
        
        Returns:
            Authentifizierungs-Header als Dictionary
        """
        headers = {"X-API-Key": self.api_key}
        
        # Einige APIs benötigen sowohl Key als auch Secret in den Headers
        if self.api_secret:
            headers["X-API-Secret"] = self.api_secret
            
        return headers
        
    def get_auth_params(self) -> Dict[str, str]:
        """Gibt die Authentifizierungs-Parameter für URL-Queries zurück.
        
        Returns:
            Authentifizierungs-Parameter als Dictionary
        """
        params = {"api_key": self.api_key}
        
        if self.api_secret:
            params["api_secret"] = self.api_secret
            
        return params
        
    def _hash_secret(self, secret: str) -> str:
        """Erstellt einen Hash des Secret für sichere Speicherung.
        
        Args:
            secret: Das zu hashende Secret
            
        Returns:
            Hash des Secrets
        """
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()
        
    def validate_secret(self, secret: str) -> bool:
        """Validiert ein API-Secret gegen den gespeicherten Hash.
        
        Args:
            secret: Das zu validierende Secret
            
        Returns:
            True, wenn das Secret gültig ist, sonst False
        """
        if "api_secret_hash" not in self.credentials:
            return False
            
        secret_hash = self._hash_secret(secret)
        return secret_hash == self.credentials["api_secret_hash"]

class APIKeyProvider(AuthProviderBase):
    """API-Key-Authentifizierungsanbieter."""
    
    def __init__(self, validate_func=None):
        """Initialisiert den API-Key-Provider.
        
        Args:
            validate_func: Optionale Funktion zur Validierung von API-Keys
        """
        super().__init__("api_key")
        self.validate_func = validate_func
        
    async def authenticate(
        self,
        api_key: str,
        api_secret: Optional[str] = None,
        expires_in: Optional[int] = None,
        key_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> APIKeySession:
        """Führt die API-Key-Authentifizierung durch.
        
        Args:
            api_key: API-Key
            api_secret: API-Secret, falls vorhanden
            expires_in: Gültigkeitsdauer in Sekunden
            key_id: ID des API-Keys
            metadata: Zusätzliche Metadaten
            
        Returns:
            APIKeySession-Objekt
            
        Raises:
            ValueError: Wenn die Validierung fehlschlägt
        """
        # Validiere den API-Key, falls eine Validierungsfunktion angegeben wurde
        if self.validate_func is not None:
            is_valid, error_msg = await self.validate_func(api_key, api_secret)
            
            if not is_valid:
                self._logger.error(f"API-Key-Validierung fehlgeschlagen: {error_msg}")
                raise ValueError(f"Ungültiger API-Key: {error_msg}")
                
        # Berechne Ablaufzeitpunkt
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            
        # Erstelle eindeutige Session-ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Erstelle Session
        session = APIKeySession(
            session_id=session_id,
            api_key=api_key,
            api_secret=api_secret,
            expires_at=expires_at,
            key_id=key_id,
            metadata=metadata
        )
        
        self._logger.info(f"Neue API-Key-Session erstellt: {session_id}")
        return session
        
    async def refresh_session(self, session: APIKeySession) -> APIKeySession:
        """Aktualisiert eine API-Key-Session.
        
        Args:
            session: Die zu aktualisierende Session
            
        Returns:
            Die unveränderte Session, da API-Keys nicht aktualisiert werden müssen
        """
        # API-Keys müssen in der Regel nicht aktualisiert werden
        return session
        
    async def validate_session(self, session: AuthSession) -> bool:
        """Validiert eine API-Key-Session.
        
        Args:
            session: Die zu validierende Session
            
        Returns:
            True, wenn die Session gültig ist, sonst False
        """
        if not isinstance(session, APIKeySession):
            return False
            
        # Prüfe, ob die Session abgelaufen ist
        if session.is_expired():
            self._logger.debug(f"Session {session.session_id} ist abgelaufen")
            return False
            
        # Bei API-Keys gibt es in der Regel keine weiteren Validierungsschritte
        # Wenn jedoch eine Validierungsfunktion angegeben wurde, verwende diese
        if self.validate_func is not None:
            try:
                is_valid, _ = await self.validate_func(
                    session.api_key,
                    session.api_secret
                )
                return is_valid
            except Exception as e:
                self._logger.error(f"Fehler bei der API-Key-Validierung: {e}")
                return False
                
        return True

class BookStackAPIKeyProvider(APIKeyProvider):
    """API-Key-Provider für BookStack."""
    
    def __init__(self, base_url: str):
        """Initialisiert den BookStack-API-Key-Provider.
        
        Args:
            base_url: Basis-URL der BookStack-Instanz
        """
        super().__init__(validate_func=self.validate_bookstack_key)
        self.base_url = base_url
        
    async def validate_bookstack_key(
        self,
        api_key: str,
        api_secret: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """Validiert einen BookStack-API-Key.
        
        Args:
            api_key: API-Key
            api_secret: API-Secret
            
        Returns:
            Tuple mit (is_valid, error_message)
        """
        import aiohttp
        
        # BookStack benötigt sowohl Key als auch Secret
        if not api_secret:
            return False, "BookStack benötigt ein API-Secret"
            
        # Erstelle URL für einen einfachen API-Aufruf
        url = f"{self.base_url}/api/books"
        
        # Erstelle Header
        headers = {
            "Authorization": f"Token {api_key}:{api_secret}",
            "Accept": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return True, None
                    elif response.status == 401:
                        return False, "Ungültige Authentifizierung"
                    else:
                        return False, f"Unerwarteter Statuscode: {response.status}"
        except Exception as e:
            return False, f"Fehler bei der API-Verbindung: {e}"

# Registriere die API-Key-Provider
register_auth_provider("api_key", APIKeyProvider)
register_auth_provider("bookstack_api_key", BookStackAPIKeyProvider)