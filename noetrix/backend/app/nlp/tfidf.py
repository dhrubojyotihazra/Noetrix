"""TF-IDF keyword extraction and unigram/bigram overlap."""

import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

from app.nlp.tokenizer import STOP_WORDS, word_boundary_match
from app.nlp.synonyms import normalize_term

# Load Taxonomy
TAXONOMY_PATH = Path(__file__).parent / "skills_taxonomy.json"
ALL_TAXONOMY_SKILLS: set[str] = set()

if TAXONOMY_PATH.exists():
    try:
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for category_skills in data.values():
                for s in category_skills:
                    ALL_TAXONOMY_SKILLS.add(s.lower())
    except Exception:
        pass


GENERIC_NON_SKILLS = {
    "learning", "machine", "years", "year", "familiarity", "experience", "experienced",
    "model", "models", "qualifications", "qualification", "minimum", "relevant", "proficient",
    "proficiency", "skills", "skill", "ability", "strong", "understanding", "working",
    "knowledge", "required", "requirements", "basic", "preferred", "role", "team",
    "engineer", "engineering", "developer", "development", "work", "responsibilities",
    "duties", "including", "plus", "bonus", "candidate", "candidates", "degree", "field",
    "quantitative", "level", "looking", "join", "help", "train", "training", "applied",
    "services", "platforms", "solutions", "position", "associate", "junior", "senior",
    "lead", "principal", "staff", "intern", "internship", "technologies", "tools",
    "track", "record", "practical", "solid", "foundation", "hands", "hands-on", "build",
    # Additional generic words and junk n-gram tokens
    "using", "used", "use", "related", "requires", "require", "seeking", "seek", "time", "times",
    "inference", "science", "ci", "cd", "real", "high", "based", "environment", "environments",
    "production", "data", "system", "systems", "project", "projects", "methods", "techniques",
    "approaches", "tasks", "task", "pipeline", "pipelines", "stack", "stacks", "architecture",
    "architectures", "infrastructure", "infrastructures", "process", "processes", "code",
    "software", "hardware"
}


def _is_filtered_noun(phrase: str) -> bool:
    """Check if phrase consists of valid nouns or noun phrases, excluding verbs/participles/adverbs."""
    words = phrase.split()
    if any(w in STOP_WORDS or w in GENERIC_NON_SKILLS for w in words):
        return False
    try:
        import nltk
        tags = nltk.pos_tag(words)
        # Must not contain verbs, adverbs, prepositions, conjunctions, pronouns
        if any(tag.startswith(("VB", "RB", "IN", "CC", "PRP", "MD")) for _, tag in tags):
            return False
        # Head word (last token) must be a noun
        return tags[-1][1].startswith("NN")
    except Exception:
        verb_adj_endings = ("ing", "ed", "ly", "able", "ible")
        if any(w.endswith(verb_adj_endings) for w in words):
            return False
        return True


def extract_jd_keywords(jd_text: str, top_n: int = 20) -> list[str]:
    """Extract top domain skills and prominent unigrams/bigrams from JD, excluding generic words."""
    if not jd_text.strip():
        return []

    found_skills: set[str] = set()

    # 1. Match against known taxonomy skills
    lower_jd = jd_text.lower()
    for skill in ALL_TAXONOMY_SKILLS:
        if skill not in GENERIC_NON_SKILLS and word_boundary_match(skill, lower_jd):
            found_skills.add(skill)

    # 2. Extract prominent n-grams via TF-IDF (filtered against generic stopwords)
    try:
        combined_stops = list(STOP_WORDS.union(GENERIC_NON_SKILLS))
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=combined_stops,
            max_features=2000
        )
        tfidf_matrix = vectorizer.fit_transform([jd_text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Sort by importance
        sorted_indices = scores.argsort()[::-1]
        for idx in sorted_indices:
            feat = feature_names[idx].strip().lower()
            words = feat.split()
            if len(feat) < 3 or feat.isnumeric():
                continue
            # Drop n-grams that contain stopwords or generic words
            if any(w in STOP_WORDS or w in GENERIC_NON_SKILLS for w in words):
                continue
            if any(len(w) < 3 for w in words):
                continue

            # Keep only taxonomy skills and filtered nouns
            if feat in ALL_TAXONOMY_SKILLS:
                found_skills.add(feat)
            elif _is_filtered_noun(feat):
                found_skills.add(feat)

            if len(found_skills) >= top_n:
                break
    except Exception:
        pass

    # Ensure no generic non-skills slip through, keeping only taxonomy skills and filtered nouns
    clean_skills = [
        s for s in found_skills
        if s not in GENERIC_NON_SKILLS and (s in ALL_TAXONOMY_SKILLS or _is_filtered_noun(s))
    ]
    return sorted(clean_skills)[:top_n]


def compute_keyword_overlap(keywords: list[str], text: str) -> tuple[list[str], list[str]]:
    """Determine matched and missing keywords against text using direct matches and synonyms."""
    from app.nlp.synonyms import get_synonyms
    lower_text = text.lower()
    matched = []
    missing = []
    for kw in keywords:
        all_variants = get_synonyms(kw)
        if any(word_boundary_match(variant, lower_text) for variant in all_variants):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing
