from db.models import Article
from services.embeddings import embed_text
from db.crud import get_similar_articles
from db.crud import upload_article
import numpy as np

def filter_article(article: Article) -> bool:
    """
    Given an article embed it and perform a database search for closest articles
    Args:
        article (Article): The article object to check.
    Returns:
        bool: True if relevant, False otherwise.
    """

    #filtered = cosine_similarity_filter(article)
    filtered = keyword_filter(article)

    if filtered:
        # If the article is relevant, upload it to the database
        upload_article(article)

    return filtered

def cosine_similarity_filter(article: Article) -> bool:
    """
    Filters an article based on cosine similarity with existing articles.
    Args:
        article (Article): The article to filter.
    Returns:
        bool: True if the article is relevant, False otherwise.
    """
    # Embed input article and fetch database
    article_embedding = embed_text(article.title)
    similar_articles = get_similar_articles(article_embedding)
    
    # Split articles into relevant and irrelevant based on the similarity results
    relevant_articles = [article[1] for article in similar_articles if article[2]['relevant'] == True]
    irrelevant_articles = [article[1] for article in similar_articles if article[2]['relevant'] == False]
    
    print(len(relevant_articles), "relevant articles found")
    print(len(irrelevant_articles), "irrelevant articles found")
    
    avg_relevant_score = np.mean(relevant_articles)
    avg_irrelevant_score = np.mean(irrelevant_articles) 
    
    print("Average relevant score:", avg_relevant_score)
    print("Average irrelevant score:", avg_irrelevant_score)
    
    if avg_relevant_score > avg_irrelevant_score:
        return True
    
    return False

def keyword_filter(article: Article) -> bool:
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