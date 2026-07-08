from dataclasses import dataclass, field
from datetime import datetime, timezone

def _now() -> datetime:
    return datetime.now()

@dataclass
class Category:
    id: str
    name: str
    slug: str
    created_at: datetime = field(default_factory=_now)