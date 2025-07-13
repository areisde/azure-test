from db import models
from services import embeddings
from db import crud
import joblib
import logging

def filter_article(article):
    """
    Given an article embed it and perform a database search for closest articles
    Args:
        article (Article): The article object to check.
    Returns:
        bool: True if relevant, False otherwise.
    """
    logging.info("Filter called")
    relevant = smart_filter(article)

    if relevant:
        # If the article is relevant, upload it to the database
        crud.upload_article(article)

    return article

def smart_filter(article, threshold=0.55):
    """
    Filters an article based on similarity to relevant or irrelevant articles
    Args:
        article (Article) : The article to filter
    Returns:
        bool: True if the article is considered relevant
    """
    classifier = joblib.load("models/it_news_filter.joblib")

    first_sentence = article["body"].split(".")[0]
    text = f"{article['title']} {first_sentence}"

    embedded_article = embeddings.embed_text(text)
    logging.info(embedded_article)
    proba  = classifier.predict_proba(embedded_article)
    label = (proba >= threshold)  
    return label

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