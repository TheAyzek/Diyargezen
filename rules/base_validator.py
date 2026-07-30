"""
Diyargezen Base TTRPG Rule Validator Contract

Architecture Strategy:
----------------------
Defines the abstract base contract (`BaseValidator`) for system-level rule validation in Diyargezen.
Follows the Strategy Pattern to decouple concrete system validators (e.g. `PF1EValidator`) from the
FastAPI web endpoints and desktop PySide6 UI controllers.

All rule checks return non-fatal diagnostic warning lists to maintain the project's Soft-Block / GM Override principle.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseValidator(ABC):
    """Base Validator class for TTRPG system rules checking."""
    
    def __init__(self, system_name: str):
        self.system_name = system_name

    @abstractmethod
    def validate(self, character: Dict[str, Any], system_data: Dict[str, Any]) -> List[str]:
        """Validates character data against system database rules.
        Returns a list of warning strings.
        """
        pass
