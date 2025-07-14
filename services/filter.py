from db import models
from services import embeddings
from db import crud
import joblib
import logging
import os
import numpy as np


def relevant_articles(articles, threshold=0.55):
    """
    Vectorizes all articles at once and predicts relevance.
    Args:
        articles (List[Article])
    Returns:
        List[bool]: Labels for each article (True = relevant)
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "it_news_filter.joblib")
    classifier = joblib.load(MODEL_PATH)

    texts = []
    for article in articles:
        first_sentence = article.body.split(".")[0]
        texts.append(f"{article.title} {first_sentence}")

    embedded_articles = np.vstack([embeddings.embed_text(t) for t in texts])
    proba = classifier.predict_proba(embedded_articles)[:, 1]
    return proba >= threshold  # returns a boolean array

def keyword_filter(article):
    """
    Filters an article based on the presence of keywords in its title or body.
    Args:
        article (Article): The article to filter.
    Returns:
        bool: True if the article contains any keyword, False otherwise.
    """
    keywords = [
        "outage", "incident", "vulnerability", "exploit", "breach",
        "cyber attack", "data leak", "security alert", "malware", "ransomware",
        "phishing", "DDoS", "zero-day", "patch", "update", "threat",
        "vulnerability disclosure", "security advisory", "cybersecurity",
        "information security", "network security", "application security",
        "cloud security", "endpoint security", "data protection", "privacy",
        "compliance", "GDPR", "HIPAA", "PCI DSS", "ISO 27001", "NIST", "CIS",
        "SOC 2", "risk management", "incident response", "forensics", "penetration testing",
        "vulnerability assessment", "security audit", "security policy", "security awareness",
        "social engineering", "insider threat", "advanced persistent threat", "APT", "threat intelligence",
        "cybersecurity framework", "cybersecurity strategy", "cybersecurity governance", "cybersecurity training",
        "cybersecurity best practices", "cybersecurity tools", "SIEM", "firewall", "IDS", "IPS", "VPN", "encryption",
        "SSL/TLS", "PKI", "digital signature", "authentication", "multi-factor authentication", "MFA", "access control",
        "identity management", "IAM", "zero trust", "network segmentation", "data loss prevention", "DLP", "endpoint detection and response", "EDR",
        "threat hunting", "security operations center", "SOC", "incident management", "security incident"
    ]
    text = f"{article.title}".lower()
    return any(keyword.lower() in text for keyword in keywords)