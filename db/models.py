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
    severity_score : float = 0
    wide_scope_score : float = 0
    high_impact_score : float = 0