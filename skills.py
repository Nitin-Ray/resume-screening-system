"""Module 2: Skills detection"""
import re

TECHNICAL = ["python", "java", "c++", "c#", "javascript", "typescript", "php", "sql", "mysql", "sqlite",
    "postgresql", "mongodb", "html", "css", "bootstrap", "react", "angular", "node.js", "flask", "django",
    "streamlit", "fastapi", "git", "github", "docker", "kubernetes", "aws", "azure", "linux", "rest api",
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "keras", "pandas", "numpy", "matplotlib", "opencv",
    "data analysis", "data structures", "algorithms", "power bi", "tableau", "excel", "cybersecurity",
    "networking", "oop", "android"]
SOFT = ["communication", "teamwork", "leadership", "problem solving", "time management", "adaptability",
        "critical thinking", "creativity", "collaboration", "presentation"]
ALL_SKILLS = TECHNICAL + SOFT
DEGREES = ["b.sc", "bsc", "b.tech", "btech", "b.e", "bca", "mca", "m.sc", "msc", "m.tech", "mtech",
           "mba", "phd", "bachelor", "master", "diploma",
           "bba", "b.com", "bcom", "m.com", "mcom", "b.a", "m.a", "b.ed", "mbbs", "b.pharm", "llb", "polytechnic"]
# Typical resume section headings
SECTION_WORDS = ["education", "experience", "skills", "projects", "objective", "summary", "certifications",
                 "internship", "qualification", "achievements", "references", "declaration"]


def find_skills(text):
    t = text.lower()
    return sorted({s for s in ALL_SKILLS
                   if re.search(r"(?<![a-z0-9+#.])" + re.escape(s) + r"(?![a-z0-9+#])", t)})


def build_profile(text):
    t = text.lower()
    # "2 years", "3+ yrs" count as experience; a single "4 year" (as in "4 year B.Tech") is a course length, so only "1 year" counts
    yrs = [int(n) for n, unit in re.findall(r"(\d+)\+?\s*(years|year|yrs)", t) if unit != "year" or int(n) == 1]
    return {"skills": find_skills(text),
            "qualifications": sorted({d for d in DEGREES if re.search(r"(?<![a-z.])" + re.escape(d) + r"(?![a-z])", t)}),
            "experience": max(yrs) if yrs else 0}


# Contact details that almost every resume has
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+\d{1,3}[\s-]?)?(?:\d{10}|\d{5}[\s-]\d{5}|\d{3}[\s-]\d{3}[\s-]\d{4})(?!\d)")


def resume_signals(text):
    """The signs that a document is a resume (True or False for each)."""
    profile = build_profile(text)
    t = text.lower()
    headings = [w for w in SECTION_WORDS if re.search(r"(?<![a-z0-9])" + w + r"(?![a-z0-9])", t)]
    return {
        "email": EMAIL_RE.search(text) is not None,
        "phone": PHONE_RE.search(text) is not None,
        "qualification": bool(profile["qualifications"]),
        "headings": len(headings) >= 2,
        "skills": len(profile["skills"]) >= 3,
    }


def looks_like_resume(text):
    """A resume shows at least two signs: e-mail, phone number, degree, resume headings, three or more skills.
    (Skills alone are not enough: technical notes also contain words like git, sql or python.)"""
    return sum(resume_signals(text).values()) >= 2
