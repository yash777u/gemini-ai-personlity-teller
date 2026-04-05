"""
🧠 Big Five (OCEAN) — AI-Powered Results via Gemini
Generates personality explanations with Indian Deadpool humor.
"""

import base64
import io
import math
import textwrap

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


# ─── Category metadata (duplicated here to stay self-contained) ──────────────

CATEGORY_META = {
    "EXT": {"name": "Extraversion",        "emoji": "🎉"},
    "AGR": {"name": "Agreeableness",       "emoji": "🤝"},
    "CSN": {"name": "Conscientiousness",   "emoji": "🎯"},
    "EST": {"name": "Emotional Stability", "emoji": "🧘"},
    "OPN": {"name": "Openness",            "emoji": "🌌"},
}

CAT_ORDER = ["EXT", "AGR", "CSN", "EST", "OPN"]


# ─── Radar / Spider Chart ────────────────────────────────────────────────────

def generate_radar_chart_base64(category_scores: dict) -> str:
    """
    Create a pentagon radar chart from category scores.
    Returns a base64-encoded PNG string.
    """
    labels = [f"{CATEGORY_META[k]['emoji']} {CATEGORY_META[k]['name']}" for k in CAT_ORDER]
    values = [category_scores[k]["pct"] for k in CAT_ORDER]

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0F0F1A")
    ax.set_facecolor("#0F0F1A")

    # Grid styling
    ax.spines["polar"].set_color("#2D2D5C")
    ax.set_thetagrids(
        [a * 180 / np.pi for a in angles[:-1]],
        labels,
        fontsize=11,
        fontweight="bold",
        color="#94A3B8",
    )
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color="#4B5563")
    ax.tick_params(axis="y", pad=10)

    # Grid lines
    for spine in ax.spines.values():
        spine.set_color("#2D2D5C")
    ax.xaxis.grid(True, color="#2D2D5C", linewidth=0.5)
    ax.yaxis.grid(True, color="#1E293B", linewidth=0.5)

    # Plot data
    ax.plot(angles, values, "o-", color="#3B82F6", linewidth=2.5, markersize=7)
    ax.fill(angles, values, alpha=0.2, color="#3B82F6")

    # Gradient-like glow
    for alpha_val, scale in [(0.08, 0.85), (0.05, 0.7)]:
        inner_values = [v * scale for v in values]
        ax.fill(angles, inner_values, alpha=alpha_val, color="#8B5CF6")

    plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="#0F0F1A", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ─── Gemini Prompt Builders ──────────────────────────────────────────────────

def _build_system_prompt() -> str:
    return textwrap.dedent("""\
        You are a friendly teacher explaining personality results to a 10-year-old.
        
        RULES:
        - Use the simplest words possible. No big words. No jargon.
        - Short sentences only. Max 10 words per sentence.
        - Use emojis to make it fun.
        - Explain like the person has never heard of psychology.
        - Be kind, positive, and encouraging always.
        - Use everyday examples like school, friends, food, games.
    """)


def _prompt_section_a(category_scores: dict, overall_pct: float) -> str:
    """Fun spider chart explanation — 120 words max."""
    scores_text = "\n".join(
        f"- {CATEGORY_META[k]['name']}: {category_scores[k]['pct']}% ({category_scores[k]['level']})"
        for k in CAT_ORDER
    )
    return textwrap.dedent(f"""\
        Here are someone's personality scores:
    {scores_text}
    
    Look at these numbers. Which ones are big? Which are small?
    Tell them what their score shape looks like in simple words.
    Example: "You are very high in X but low in Y. That means..."
    Use examples from everyday life like school or playing with friends.
    STRICT LIMIT: 5 bullet points. One simple sentence each.
    """)


def _prompt_section_b(overall_pct: float, overall_level: str) -> str:
    """Overall personality meaning — 100 words max."""
    return textwrap.dedent(f"""\
        Someone scored {overall_pct}% overall in a personality test. Level: {overall_level}.
    
    Explain what kind of person they are in the simplest way.
    Use examples: "You are like someone who always helps friends" or "You love trying new games".
    No big words. Write like a story for a child.
    STRICT LIMIT: 4 bullet points. One simple sentence each.
    """)


def _prompt_section_c(category_scores: dict) -> str:
    """Category-wise breakdown — 80 words per category."""
    sections = []
    for k in CAT_ORDER:
        s = category_scores[k]
        meta = CATEGORY_META[k]
        sections.append(
            f"{meta['emoji']} {meta['name']}: {s['pct']}% ({s['level']})"
        )
    scores_text = "\n".join(sections)

    return textwrap.dedent(f"""\
        Here are 5 personality scores:
    {scores_text}
    
    For EACH one, explain it in ONE simple sentence a child can understand.
    Use everyday examples. Like: "This means you love talking to new people!" 
    or "This means you always finish your homework on time!"
    
    Format: emoji + trait name as heading, then one sentence below it.
    STRICT LIMIT: 1 sentence per trait. Easiest words only.
    """)


def _prompt_section_d(flags: list) -> str:
    """Unusual patterns — 25 words max."""
    if not flags:
        return textwrap.dedent("""\
            This person answered all questions honestly and carefully.
    
    Tell them their results are trustworthy in simple, happy words.
    Tell them one tip on how to use their results to improve themselves.
    Write like you are talking to a child. Keep it short and kind.
    STRICT LIMIT: 3 bullet points max.
        """)

    flags_text = "\n".join(f"- {f}" for f in flags)
    return textwrap.dedent(f"""\
        Some answers in the test looked unusual:
    {flags_text}
    
    Explain this in simple words. Like: "Some of your answers were a bit mixed up."
    Tell them it is okay and suggest they try again more carefully.
    Be kind. No blame. Write like talking to a child.
    STRICT LIMIT: 3 bullet points max.
    """)


# ─── Gemini API Calls ────────────────────────────────────────────────────────

def generate_results(api_key: str, scores: dict) -> dict:
    """
    Call Gemini for all 4 sections. Returns a dict with keys a, b, c, d.
    Each value is the generated text string.

    Args:
        api_key: Gemini API key
        scores: output from scoring.calculate_scores()

    Returns:
        {"a": str, "b": str, "c": str, "d": str}
        On error, returns {"error": str}
    """
    try:
        import google.generativeai as genai
    except ImportError:
        return {"error": "google-generativeai package not installed. Run: pip install google-generativeai"}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=_build_system_prompt(),
        )
    except Exception as e:
        return {"error": f"Failed to configure Gemini: {str(e)}"}

    cat_scores = scores["category_scores"]
    overall_pct = scores["overall_pct"]
    overall_level = scores["overall_level"]
    flags = scores["flags"]

    prompts = {
        "a": _prompt_section_a(cat_scores, overall_pct),
        "b": _prompt_section_b(overall_pct, overall_level),
        "c": _prompt_section_c(cat_scores),
        "d": _prompt_section_d(flags),
    }

    results = {}
    for key, prompt in prompts.items():
        try:
            response = model.generate_content(prompt)
            results[key] = response.text.strip()
        except Exception as e:
            results[key] = f"⚠️ Error generating this section: {str(e)}"

    return results
