import uuid
from dataclasses import dataclass, field



@dataclass
class Mensaje:
    origen: str
    destino: str
    tipo: str
    payload: dict[str, any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # id unico para identificar el paquete