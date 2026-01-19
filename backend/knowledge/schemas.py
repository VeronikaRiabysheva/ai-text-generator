from dataclasses import dataclass
from typing import Optional, List


@dataclass
class KnowledgeEntity:
    entity_type: str
    name: str
    description: Optional[str]
    module: str
    relations: List[str]
