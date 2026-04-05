"""
🧠 Big Five (OCEAN) Scoring Engine
Pure logic — no UI, no API calls. Just math.
"""

from statistics import stdev
from collections import Counter


# ─── Score Levels ─────────────────────────────────────────────────────────────

def _pct_to_level(pct: float) -> str:
    """Convert a 0-100 percentage to a human label."""
    if pct >= 80:
        return "Very High"
    elif pct >= 60:
        return "High"
    elif pct >= 40:
        return "Moderate"
    elif pct >= 20:
        return "Low"
    else:
        return "Very Low"


# ─── Core Score Calculation ───────────────────────────────────────────────────

def _compute_item_score(raw_answer: int, direction: str) -> int:
    """
    Positive (+): score = raw answer (1-5)
    Negative (-): score = 6 - raw answer
    """
    if direction == "+":
        return raw_answer
    else:
        return 6 - raw_answer


def _compute_category_scores(responses: dict, questions: list) -> dict:
    """
    Compute raw score and percentage for each category.
    responses: {question_id: raw_answer (1-5)}
    questions: list of question dicts from question.txt
    Returns: {category_key: {"raw": int, "pct": float, "level": str}}
    """
    # Group questions by category
    categories = {}
    for q in questions:
        cat = q["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)

    result = {}
    for cat_key, cat_questions in categories.items():
        raw_total = 0
        answered_count = 0
        for q in cat_questions:
            if q["id"] in responses:
                raw_answer = responses[q["id"]]
                raw_total += _compute_item_score(raw_answer, q["direction"])
                answered_count += 1

        # Raw score range: 10 (all 1s after adjustment) to 50 (all 5s)
        # Convert to 0-100%: (raw - 10) / 40 * 100
        if answered_count > 0:
            # Scale proportionally if not all questions answered
            expected_questions = len(cat_questions)
            if answered_count < expected_questions:
                # Extrapolate: raw_total / answered * expected
                raw_total = round(raw_total / answered_count * expected_questions)

            pct = max(0.0, min(100.0, (raw_total - 10) / 40 * 100))
        else:
            raw_total = 0
            pct = 0.0

        result[cat_key] = {
            "raw": raw_total,
            "pct": round(pct, 1),
            "level": _pct_to_level(pct),
        }

    return result


# ─── Unusual Pattern / Liar Detection ────────────────────────────────────────

def _detect_flags(responses: dict, questions: list) -> list:
    """
    Detect suspicious answer patterns.
    Returns a list of human-readable flag strings.
    """
    if len(responses) < 10:
        return []

    flags = []
    raw_answers = list(responses.values())

    # 1. All-same responses
    unique_vals = set(raw_answers)
    if len(unique_vals) == 1:
        val = raw_answers[0]
        flags.append(
            f"🚩 Every single answer is {val}. That's suspicious — "
            f"real people have varied preferences."
        )

    # 2. Extreme responder — >80% are 1 or 5
    extreme_count = sum(1 for a in raw_answers if a in (1, 5))
    extreme_pct = extreme_count / len(raw_answers)
    if extreme_pct > 0.80 and len(unique_vals) > 1:
        flags.append(
            f"🚩 {round(extreme_pct * 100)}% of answers are extreme (1 or 5). "
            f"Most people use the middle range too."
        )

    # 3. Contradictory pairs within same category
    # Build question lookup
    q_lookup = {q["id"]: q for q in questions}
    cats = {}
    for q in questions:
        c = q["category"]
        if c not in cats:
            cats[c] = []
        cats[c].append(q)

    contradiction_cats = []
    for cat_key, cat_qs in cats.items():
        pos_qs = [q for q in cat_qs if q["direction"] == "+" and q["id"] in responses]
        neg_qs = [q for q in cat_qs if q["direction"] == "-" and q["id"] in responses]

        if pos_qs and neg_qs:
            avg_pos = sum(responses[q["id"]] for q in pos_qs) / len(pos_qs)
            avg_neg = sum(responses[q["id"]] for q in neg_qs) / len(neg_qs)
            # If both positive and negative questions have high raw scores,
            # that's contradictory (high on "I start conversations" AND
            # high on "I don't talk a lot")
            if avg_pos >= 4.0 and avg_neg >= 4.0:
                contradiction_cats.append(cat_key)
            elif avg_pos <= 2.0 and avg_neg <= 2.0:
                contradiction_cats.append(cat_key)

    if contradiction_cats:
        from_names = {
            "EXT": "Extraversion", "AGR": "Agreeableness",
            "CSN": "Conscientiousness", "EST": "Emotional Stability",
            "OPN": "Openness",
        }
        cat_names = [from_names.get(c, c) for c in contradiction_cats]
        flags.append(
            f"🚩 Contradictory answers detected in: {', '.join(cat_names)}. "
            f"Opposite statements got similar scores."
        )

    # 4. Near-zero variance — stdev < 0.5
    if len(raw_answers) >= 10 and len(unique_vals) > 1:
        sd = stdev(raw_answers)
        if sd < 0.5:
            flags.append(
                f"🚩 Almost no variation in answers (std dev: {sd:.2f}). "
                f"Responses look robotically uniform."
            )

    # 5. Perfectly alternating pattern
    if len(raw_answers) >= 10:
        # Check if answers repeat a cycle of length 1-3
        for cycle_len in [2, 3]:
            cycle = raw_answers[:cycle_len]
            is_repeating = True
            for i, a in enumerate(raw_answers):
                if a != cycle[i % cycle_len]:
                    is_repeating = False
                    break
            if is_repeating:
                flags.append(
                    f"🚩 Answers follow a repeating pattern: "
                    f"{' → '.join(str(x) for x in cycle)} (cycle of {cycle_len}). "
                    f"That's not how real opinions work."
                )
                break

    return flags


# ─── Public API ───────────────────────────────────────────────────────────────

def calculate_scores(responses: dict, questions: list) -> dict:
    """
    Main entry point. Compute everything.

    Args:
        responses: {question_id: raw_answer_int}
        questions: list of question dicts from question.txt

    Returns:
        {
            "category_scores": {cat_key: {"raw", "pct", "level"}},
            "overall_pct": float,
            "overall_level": str,
            "flags": [str, ...],
            "flag_count": int,
        }
    """
    cat_scores = _compute_category_scores(responses, questions)

    # Overall = average of all category percentages
    if cat_scores:
        overall_pct = round(
            sum(s["pct"] for s in cat_scores.values()) / len(cat_scores), 1
        )
    else:
        overall_pct = 0.0

    flags = _detect_flags(responses, questions)

    return {
        "category_scores": cat_scores,
        "overall_pct": overall_pct,
        "overall_level": _pct_to_level(overall_pct),
        "flags": flags,
        "flag_count": len(flags),
    }
