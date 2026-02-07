def render_arguments_md(title: str, items: list):
    md = f"### {title}\n\n"

    for idx, item in enumerate(items, 1):
        md += f"**{idx}. {item['point']}**\n\n"

        score = item.get("score", {})
        if score:
            md += (
                f"- Clarity: {score.get('clarity', score.get('strength', 'N/A'))}\n"
                f"- Evidence/Risk: {score.get('evidence', score.get('risk', 'N/A'))}\n"
                f"- Relevance/Rejection Likelihood: "
                f"{score.get('relevance', score.get('likelihood_of_rejection', 'N/A'))}\n"
                f"- **Total Score: {score.get('total', 'N/A')} / 15**\n\n"
            )

    return md
def render_rebuttals_md(title: str, rebuttals: list, key: str):
    md = f"### {title}\n\n"

    for idx, item in enumerate(rebuttals, 1):
        md += f"**{idx}. Against:** {item['against']}\n\n"
        md += f"**Response:** {item[key]}\n\n"

        score = item.get("improved_score", {})
        if score:
            md += (
                f"- Improved Clarity/Strength: {score.get('clarity', score.get('strength', 'N/A'))}\n"
                f"- Evidence/Risk: {score.get('evidence', score.get('risk', 'N/A'))}\n"
                f"- Relevance/Rejection Likelihood: "
                f"{score.get('relevance', score.get('likelihood_of_rejection', 'N/A'))}\n"
                f"- **New Score: {score.get('total', 'N/A')} / 15**\n\n"
            )

    return md
def render_legal_md(legal_json: dict):
    md = "### ⚖️ Legal Assessment (Indian Law)\n\n"

    assessments = legal_json.get("legal_assessment", [])

    if not assessments:
        md += "_No applicable legal provisions were identified._"
        return md

    for idx, item in enumerate(assessments, 1):
        status = item.get("status", "").lower()

        if status == "valid":
            status_icon = "✅ Valid"
        elif status == "weak":
            status_icon = "⚠️ Weak"
        else:
            status_icon = "❌ Invalid"

        md += f"**{idx}. {item.get('argument', 'N/A')}**\n\n"
        md += f"- **Status:** {status_icon}\n"
        md += f"- **Law:** {item.get('law', 'N/A')}\n"
        md += f"- **Reason:** {item.get('reason', 'N/A')}\n\n"

    return md
