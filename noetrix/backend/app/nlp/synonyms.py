"""Synonym normalization dictionary and canonical lookup."""

SYNONYM_MAP: dict[str, str] = {
    # Languages & Frameworks
    "js": "javascript",
    "ts": "typescript",
    "golang": "go",
    "py": "python",
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "nodejs": "node.js",
    "node": "node.js",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    
    # Cloud & DevOps
    "aws": "amazon web services",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "k8s": "kubernetes",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    
    # DB
    "postgres": "postgresql",
    "mongo": "mongodb",
    "elastic": "elasticsearch",
    "es": "elasticsearch",
    
    # AI / ML
    "ml": "machine learning",
    "dl": "deep learning",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "llms": "llm",
    "large language models": "llm",
    "nlp": "natural language processing",
    "natural language processing": "nlp",
    "transformers": "hugging face",
    "huggingface": "hugging face",
    "distilbert": "transformers",
    "bert": "transformers",
    "opencv": "computer vision",
    "cv": "computer vision",
    
    # Dev & Version Control
    "github": "git",
    "gitlab": "git",
    
    # Methodologies & Roles
    "pm": "product management",
    "qa": "quality assurance",
    "swe": "software engineer",
    "sde": "software development engineer",
}


def normalize_term(term: str) -> str:
    """Normalize term to canonical form."""
    clean = term.strip().lower()
    return SYNONYM_MAP.get(clean, clean)


def get_synonyms(term: str) -> list[str]:
    """Get all known synonyms for a term including itself."""
    norm = normalize_term(term)
    results = {term.lower(), norm}
    for k, v in SYNONYM_MAP.items():
        if v == norm or k == norm:
            results.add(k)
            results.add(v)
    return list(results)
