from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Detector(ABC):
    name: str

    @abstractmethod
    def run(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
