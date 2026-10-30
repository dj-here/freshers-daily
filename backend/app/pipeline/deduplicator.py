import re
from difflib import SequenceMatcher
from typing import List, Optional

def normalize_title(title: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    # Remove common fluff words
    fluff = ["freshers", "graduate", "batch", "intern", "engineer", "software", "india", "opportunity", "hiring", "immediate", "urgent"]
    tokens = [w for w in cleaned.split() if w not in fluff]
    return " ".join(tokens)

def compute_text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate_listing(
    title1: str,
    city1: str,
    title2: str,
    city2: str,
    threshold: float = 0.92
) -> bool:
    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)
    if norm1 == norm2 and city1.lower() == city2.lower():
        return True
    
    sim = compute_text_similarity(title1, title2)
    if sim >= threshold and (city1.lower() == city2.lower() or city1 == "Pan India" or city2 == "Pan India"):
        return True

    return False
