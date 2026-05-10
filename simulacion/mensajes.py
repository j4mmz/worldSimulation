from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Mensaje:
    origen: str
    destino: str
    tipo: str
    payload: Dict[str, Any]