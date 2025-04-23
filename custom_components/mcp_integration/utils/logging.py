"""
Erweiterte Logging-Funktionalität für die MCP Integration Suite.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - logging
  - os
  - enum
  - datetime

TODO:
  - Integration von kontextbezogenem Logging
  - Implementierung von Logging-Rotation
  - Erweiterung um strukturiertes Logging
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import os
import enum
import logging
import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, Union

from ..const import LOG_DIR, LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR

# Log-Level-Enum
class LogLevel(enum.Enum):
    """Enum für Log-Level."""
    DEBUG = LOG_LEVEL_DEBUG
    INFO = LOG_LEVEL_INFO
    WARNING = LOG_LEVEL_WARNING
    ERROR = LOG_LEVEL_ERROR
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Konvertiert einen String in ein LogLevel.
        
        Args:
            level_str: String-Repräsentation des Log-Levels
            
        Returns:
            LogLevel-Enum
            
        Raises:
            ValueError: Wenn der String kein gültiges Log-Level ist
        """
        for level in cls:
            if level.value == level_str.lower():
                return level
                
        raise ValueError(f"Ungültiges Log-Level: {level_str}")
    
    def to_logging_level(self) -> int:
        """Konvertiert das LogLevel in einen logging-Level-Integer.
        
        Returns:
            Entsprechender logging-Level als Integer
        """
        level_map = {
            self.DEBUG: logging.DEBUG,
            self.INFO: logging.INFO,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR
        }
        return level_map[self]

def ensure_log_dir() -> None:
    """Stellt sicher, dass das Log-Verzeichnis existiert."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        logging.info(f"Log-Verzeichnis erstellt: {LOG_DIR}")

def setup_logger(
    name: str,
    level: Union[LogLevel, str] = LogLevel.INFO,
    file_logging: bool = True,
    console_logging: bool = True,
    log_format: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """Richtet einen Logger ein.
    
    Args:
        name: Name des Loggers
        level: Log-Level
        file_logging: Ob in eine Datei geloggt werden soll
        console_logging: Ob auf die Konsole geloggt werden soll
        log_format: Format der Log-Nachrichten
        max_file_size: Maximale Größe der Log-Datei in Bytes
        backup_count: Anzahl der zu behaltenden Backup-Dateien
        
    Returns:
        Der konfigurierte Logger
    """
    # Konvertiere String-Level in LogLevel-Enum
    if isinstance(level, str):
        level = LogLevel.from_string(level)
        
    # Erstelle Logger
    logger = logging.getLogger(name)
    logger.setLevel(level.to_logging_level())
    
    # Lösche existierende Handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Standard-Log-Format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
    formatter = logging.Formatter(log_format)
    
    # Datei-Logging
    if file_logging:
        ensure_log_dir()
        
        log_file = os.path.join(LOG_DIR, f"{name}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Konsolen-Logging
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

class ContextLogger:
    """Logger mit Kontext-Tracking für zusammenhängende Log-Nachrichten."""
    
    def __init__(self, logger: logging.Logger):
        """Initialisiert einen ContextLogger.
        
        Args:
            logger: Der Basis-Logger
        """
        self.logger = logger
        self.context: Dict[str, Any] = {}
        
    def set_context(self, **kwargs) -> None:
        """Setzt den Kontext für zukünftige Log-Nachrichten.
        
        Args:
            **kwargs: Schlüssel-Wert-Paare für den Kontext
        """
        self.context.update(kwargs)
        
    def clear_context(self) -> None:
        """Löscht den aktuellen Kontext."""
        self.context.clear()
        
    def _format_with_context(self, msg: str) -> str:
        """Formatiert eine Nachricht mit dem aktuellen Kontext.
        
        Args:
            msg: Die zu formatierende Nachricht
            
        Returns:
            Die formatierte Nachricht
        """
        if not self.context:
            return msg
            
        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{msg} [Context: {context_str}]"
        
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Loggt eine Debug-Nachricht mit Kontext.
        
        Args:
            msg: Die zu loggende Nachricht
            *args: Argumente für die Formatierung
            **kwargs: Schlüssel-Wert-Paare für die Formatierung
        """
        self.logger.debug(self._format_with_context(msg), *args, **kwargs)
        
    def info(self, msg: str, *args, **kwargs) -> None:
        """Loggt eine Info-Nachricht mit Kontext.
        
        Args:
            msg: Die zu loggende Nachricht
            *args: Argumente für die Formatierung
            **kwargs: Schlüssel-Wert-Paare für die Formatierung
        """
        self.logger.info(self._format_with_context(msg), *args, **kwargs)
        
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Loggt eine Warning-Nachricht mit Kontext.
        
        Args:
            msg: Die zu loggende Nachricht
            *args: Argumente für die Formatierung
            **kwargs: Schlüssel-Wert-Paare für die Formatierung
        """
        self.logger.warning(self._format_with_context(msg), *args, **kwargs)
        
    def error(self, msg: str, *args, **kwargs) -> None:
        """Loggt eine Error-Nachricht mit Kontext.
        
        Args:
            msg: Die zu loggende Nachricht
            *args: Argumente für die Formatierung
            **kwargs: Schlüssel-Wert-Paare für die Formatierung
        """
        self.logger.error(self._format_with_context(msg), *args, **kwargs)
        
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Loggt eine Exception mit Kontext.
        
        Args:
            msg: Die zu loggende Nachricht
            *args: Argumente für die Formatierung
            **kwargs: Schlüssel-Wert-Paare für die Formatierung
        """
        self.logger.exception(self._format_with_context(msg), *args, **kwargs)

def get_context_logger(name: str, **kwargs) -> ContextLogger:
    """Erstellt einen ContextLogger.
    
    Args:
        name: Name des Loggers
        **kwargs: Initialer Kontext
        
    Returns:
        ContextLogger-Instanz
    """
    logger = logging.getLogger(name)
    context_logger = ContextLogger(logger)
    
    if kwargs:
        context_logger.set_context(**kwargs)
        
    return context_logger