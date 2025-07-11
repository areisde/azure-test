from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Source:
    name: str
    url: str
    type: str

@dataclass
class Article:
    id: str
    title: str
    body: str
    published_at: Optional[str]
    url: Optional[str] = None
    source : str = None
    created_at: Optional[str] = None

@dataclass
class Filter:
    embedding: List[float]
    relevant: bool
    url: str