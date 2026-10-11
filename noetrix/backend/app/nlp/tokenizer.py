"""Tokenization, boundary matching, regex metrics, and acronym sanitization."""

import re

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
    "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his",
    "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves",
    # Additional generic stopwords & verbs
    "using", "uses", "used", "use", "related", "requires", "require", "required", "seeking", "seek", "seeks",
    "looking", "look", "across", "within", "per", "via", "etc", "eg", "ie", "including", "includes", "included",
    "well", "also", "able", "like", "either"
}

# Blocklist to avoid false-positive tech skills
ACRONYM_BLOCKLIST = {
    "GPA", "CGPA", "SAT", "ACT", "GRE", "GMAT", "USA", "UK", "US", "EU",
    "INC", "LLC", "LTD", "CORP", "CO", "JAN", "FEB", "MAR", "APR", "MAY",
    "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "THE", "AND", "FOR",
    "OUT", "NEW", "ALL", "NOT", "YES", "III", "IV", "VII", "VIII", "XVI"
}

# 63 high-impact action verbs (from ATSify pattern)
ACTION_VERBS = {
    "accelerated", "achieved", "acquired", "administered", "advanced", "analyzed",
    "architected", "automated", "boosted", "built", "centralized", "championed",
    "collaborated", "constructed", "created", "decreased", "delivered", "deployed",
    "designed", "developed", "directed", "eliminated", "enabled", "engineered",
    "established", "executed", "expanded", "expedited", "formulated", "founded",
    "generated", "grew", "guided", "implemented", "improved", "increased",
    "initiated", "innovated", "instituted", "integrated", "introduced", "launched",
    "lead", "led", "managed", "maximized", "migrated", "minimized", "modernized",
    "negotiated", "optimized", "orchestrated", "overhauled", "pioneered", "reduced",
    "refactored", "resolved", "restructured", "revamped", "scaled", "spearheaded",
    "streamlined", "transformed", "unified"
}

# 10 strict quantification patterns
QUANTIFICATION_PATTERNS = [
    re.compile(r"\b\d+(\.\d+)?\s*%", re.IGNORECASE),                         # 45%, 3.5%
    re.compile(r"\$[\d,]+(\.\d+)?\s*([kmb]|million|billion)?\b", re.IGNORECASE), # $2M, $500k
    re.compile(r"\b\d+(\.\d+)?\s*[xX]\b"),                                   # 3x, 10x
    re.compile(r"\b\d{2,}\+?\s*(users?|customers?|clients?|members?|engineers?|developers?|requests?|queries|records?)\b", re.IGNORECASE),
    re.compile(r"\b(saved|reduced|cut|decreased|increased|boosted|grew)\b.*\b\d+(\.\d+)?\b", re.IGNORECASE),
    re.compile(r"\b\d+\+?\s*(hours?|days?|weeks?|months?|minutes?|ms|seconds?)\b", re.IGNORECASE),
    re.compile(r"\b(top|first|#1|ranked)\s*\d+\b", re.IGNORECASE),
    re.compile(r"\bover\s+\d{2,}\b", re.IGNORECASE),
    re.compile(r"\bfrom\s+\d+.*to\s+\d+\b", re.IGNORECASE),
    re.compile(r"\b\d{1,3}(,\d{3})+\b")                                       # 100,000+
]


def word_boundary_match(term: str, text: str) -> bool:
    """Exact word-boundary regex match, safe for symbols like c++, c#, .net."""
    if not term or not text:
        return False
    escaped = re.escape(term.strip().lower())
    # Allow leading/trailing non-alphanumeric boundaries
    pattern = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
    return bool(re.search(pattern, text.lower()))


def count_quantified_bullets(bullets: list[str]) -> tuple[int, list[str]]:
    """Count bullets that contain verified metrics."""
    quantified = []
    for b in bullets:
        if any(p.search(b) for p in QUANTIFICATION_PATTERNS):
            quantified.append(b)
    return len(quantified), quantified


def count_action_verbs(bullets: list[str]) -> int:
    """Count bullets starting with or containing strong action verbs."""
    count = 0
    for b in bullets:
        words = re.findall(r"\b[a-zA-Z]+\b", b.lower())
        if words and any(w in ACTION_VERBS for w in words[:3]):
            count += 1
    return count
