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
