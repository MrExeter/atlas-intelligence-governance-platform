from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class RawSource:
    url: str
    title: str
    content: str
    provider: str
    raw_metadata: Dict[str, Any] = field(default_factory=dict)