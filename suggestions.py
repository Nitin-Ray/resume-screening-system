"""Module 4: Missing skills & suggestions"""


def get_suggestions(missing, score):
    tips = [f"Add '{s}' to your skills/projects section if you know it, otherwise learn it." for s in missing]
    if score < 40:
        tips.append("Low match: tailor your resume using keywords from the job description.")
    elif score < 70:
        tips.append("Decent match: add more relevant projects and measurable achievements.")
    else:
        tips.append("Strong match: keep the resume concise and highlight your best projects.")
    return tips
