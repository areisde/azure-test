from dataclasses import dataclass

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
    published_at: str
    url: str = ""
    source : str = ""
    created_at: str = ""