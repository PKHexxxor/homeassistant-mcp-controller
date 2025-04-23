"""
Checkpoint-Mechanismen für die autonome Entwicklung.

Status: PARTIAL
Version: 0.1.0
Checkpoint: CHECKPOINT-INITIAL
Letztes Update: 2023-04-24

Abhängigkeiten:
  - os
  - json
  - logging
  - datetime
  - typing

TODO:
  - Erweiterung um Checkpoint-Wiederherstellung
  - Integration von Abhängigkeits-Tracking
  - Implementierung von Entwicklungs-Metriken
"""

__version__ = "0.1.0"
__status__ = "development"
__last_updated__ = "2023-04-24"

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..const import CHECKPOINT_DIR

# Setup logging
_LOGGER = logging.getLogger(__name__)

@dataclass
class Checkpoint:
    """Repräsentiert einen Entwicklungs-Checkpoint."""
    
    name: str
    status: str
    description: str
    timestamp: datetime.datetime
    dependencies: List[str]
    next_steps: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Checkpoint in ein Dictionary.
        
        Returns:
            Dictionary-Repräsentation des Checkpoints
        """
        return {
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "dependencies": self.dependencies,
            "next_steps": self.next_steps,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Erstellt einen Checkpoint aus einem Dictionary.
        
        Args:
            data: Dictionary mit Checkpoint-Daten
            
        Returns:
            Checkpoint-Objekt
        """
        return cls(
            name=data["name"],
            status=data["status"],
            description=data["description"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            dependencies=data["dependencies"],
            next_steps=data["next_steps"],
            metadata=data["metadata"]
        )

def ensure_checkpoint_dir() -> None:
    """Stellt sicher, dass das Checkpoint-Verzeichnis existiert."""
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)
        _LOGGER.info(f"Checkpoint-Verzeichnis erstellt: {CHECKPOINT_DIR}")

def set_checkpoint(
    name: str,
    status: str = "COMPLETE",
    description: str = "",
    dependencies: List[str] = None,
    next_steps: List[str] = None,
    metadata: Dict[str, Any] = None
) -> Checkpoint:
    """Setzt einen neuen Checkpoint.
    
    Args:
        name: Name des Checkpoints
        status: Status des Checkpoints (COMPLETE, PARTIAL, etc.)
        description: Beschreibung des Checkpoints
        dependencies: Liste der abgeschlossenen Abhängigkeiten
        next_steps: Liste der nächsten Implementierungsschritte
        metadata: Zusätzliche Metadaten
        
    Returns:
        Der erstellte Checkpoint
    """
    ensure_checkpoint_dir()
    
    checkpoint = Checkpoint(
        name=name,
        status=status,
        description=description,
        timestamp=datetime.datetime.now(),
        dependencies=dependencies or [],
        next_steps=next_steps or [],
        metadata=metadata or {}
    )
    
    filename = os.path.join(CHECKPOINT_DIR, f"{name}.json")
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(checkpoint.to_dict(), f, indent=2)
        
    _LOGGER.info(f"Checkpoint gesetzt: {name}")
    
    return checkpoint

def get_checkpoint(name: str) -> Optional[Checkpoint]:
    """Liest einen Checkpoint aus dem Dateisystem.
    
    Args:
        name: Name des Checkpoints
        
    Returns:
        Der gelesene Checkpoint oder None, wenn er nicht existiert
    """
    filename = os.path.join(CHECKPOINT_DIR, f"{name}.json")
    
    if not os.path.exists(filename):
        _LOGGER.warning(f"Checkpoint nicht gefunden: {name}")
        return None
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        checkpoint = Checkpoint.from_dict(data)
        _LOGGER.debug(f"Checkpoint geladen: {name}")
        return checkpoint
        
    except Exception as e:
        _LOGGER.error(f"Fehler beim Laden des Checkpoints {name}: {e}")
        return None

def list_checkpoints() -> List[str]:
    """Gibt eine Liste aller verfügbaren Checkpoints zurück.
    
    Returns:
        Liste der Checkpoint-Namen
    """
    ensure_checkpoint_dir()
    
    checkpoints = []
    for filename in os.listdir(CHECKPOINT_DIR):
        if filename.endswith(".json"):
            checkpoints.append(filename[:-5])  # Entferne ".json"
            
    return checkpoints

def validate_checkpoint(name: str) -> Tuple[bool, Optional[str]]:
    """Validiert einen Checkpoint.
    
    Args:
        name: Name des Checkpoints
        
    Returns:
        Tuple mit (is_valid, error_message)
    """
    checkpoint = get_checkpoint(name)
    
    if checkpoint is None:
        return False, f"Checkpoint {name} nicht gefunden"
        
    # Validiere Status
    if checkpoint.status not in ["COMPLETE", "PARTIAL", "REVIEW"]:
        return False, f"Ungültiger Status: {checkpoint.status}"
        
    # Validiere Timestamp
    if checkpoint.timestamp > datetime.datetime.now():
        return False, f"Timestamp liegt in der Zukunft: {checkpoint.timestamp}"
        
    # Alle Validierungen bestanden
    return True, None

def get_last_checkpoint() -> Optional[Checkpoint]:
    """Gibt den letzten gesetzten Checkpoint zurück.
    
    Returns:
        Der letzte Checkpoint oder None, wenn kein Checkpoint existiert
    """
    checkpoints = list_checkpoints()
    
    if not checkpoints:
        return None
        
    # Lade alle Checkpoints
    all_checkpoints = []
    for name in checkpoints:
        checkpoint = get_checkpoint(name)
        if checkpoint:
            all_checkpoints.append(checkpoint)
            
    # Sortiere nach Timestamp
    all_checkpoints.sort(key=lambda c: c.timestamp, reverse=True)
    
    return all_checkpoints[0] if all_checkpoints else None

def get_checkpoints_by_phase(phase: str) -> List[Checkpoint]:
    """Gibt alle Checkpoints für eine bestimmte Phase zurück.
    
    Args:
        phase: Name der Phase (z.B. "P1", "P2", etc.)
        
    Returns:
        Liste der Checkpoints für die Phase
    """
    checkpoints = list_checkpoints()
    
    result = []
    for name in checkpoints:
        if name.startswith(f"CHECKPOINT-{phase}"):
            checkpoint = get_checkpoint(name)
            if checkpoint:
                result.append(checkpoint)
                
    return result

def is_dependency_satisfied(dependency: str) -> bool:
    """Prüft, ob eine Abhängigkeit erfüllt ist.
    
    Args:
        dependency: Name der Abhängigkeit
        
    Returns:
        True, wenn die Abhängigkeit erfüllt ist, sonst False
    """
    # Format: "checkpoint:name"
    if ":" not in dependency:
        return False
        
    dependency_type, dependency_name = dependency.split(":", 1)
    
    if dependency_type == "checkpoint":
        checkpoint = get_checkpoint(dependency_name)
        return checkpoint is not None and checkpoint.status == "COMPLETE"
        
    return False

def check_dependencies(dependencies: List[str]) -> Tuple[bool, List[str]]:
    """Prüft, ob alle Abhängigkeiten erfüllt sind.
    
    Args:
        dependencies: Liste der Abhängigkeiten
        
    Returns:
        Tuple mit (all_satisfied, unsatisfied_dependencies)
    """
    unsatisfied = []
    
    for dependency in dependencies:
        if not is_dependency_satisfied(dependency):
            unsatisfied.append(dependency)
            
    return len(unsatisfied) == 0, unsatisfied

def create_initial_checkpoint() -> Checkpoint:
    """Erstellt den initialen Checkpoint, falls er noch nicht existiert.
    
    Returns:
        Der initiale Checkpoint
    """
    # Prüfe, ob der initiale Checkpoint bereits existiert
    initial_checkpoint = get_checkpoint("CHECKPOINT-INITIAL")
    
    if initial_checkpoint is not None:
        return initial_checkpoint
    
    # Erstelle den initialen Checkpoint
    return set_checkpoint(
        name="CHECKPOINT-INITIAL",
        status="COMPLETE",
        description="Initialer Checkpoint für die Home Assistant MCP Integration Suite",
        next_steps=[
            "Implementierung der Core-Framework-Komponenten",
            "Aufbau der Authentifizierungsschicht",
            "Vorbereitung der Server-Integration"
        ],
        metadata={
            "phase": "initialization",
            "created_by": "checkpointing.py"
        }
    )
