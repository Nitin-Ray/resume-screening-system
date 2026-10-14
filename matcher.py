"""Module 3: Job description matching (TF-IDF + skill overlap)"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills import find_skills


def match_score(resume, jd):
    r_sk, j_sk = set(find_skills(resume)), set(find_skills(jd))
    skill_pct = len(r_sk & j_sk) / len(j_sk) * 100 if j_sk else None  # None: the JD names no known skill
    try:
        vec = TfidfVectorizer(stop_words="english").fit_transform([resume, jd])
        text_pct = cosine_similarity(vec[0], vec[1])[0][0] * 100
    except ValueError:
        text_pct = 0
    if skill_pct is None:  # nothing to compare skill by skill, so the text similarity alone gives the score
        final = round(text_pct, 1)
    else:
        final = round(0.6 * skill_pct + 0.4 * text_pct, 1)
    return {"score": final, "skill_pct": None if skill_pct is None else round(skill_pct, 1), "text_pct": round(text_pct, 1),
            "matched": sorted(r_sk & j_sk), "missing": sorted(j_sk - r_sk)}
