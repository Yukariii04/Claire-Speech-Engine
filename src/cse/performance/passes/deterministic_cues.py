"""PRD-026: Deterministic Textual Cue Detection.

Detects punctuation, capitalization, and lexical cues from utterance text.
Applies combination rules with explicit priority ordering.
Only runs when no explicit tag is present.
"""
import re

# ─── Punctuation cue mappings — PRD-026 §8.1 ───

PUNCTUATION_CUES = {
    "?!": {
        "primary_intent": "exclamation",
        "pace": "fast",
        "pitch_contour": "peaked",
        "emphasis": "throughout",
    },
    "!!!": {
        "primary_intent": "exclamation",
        "pace": "fast",
        "pitch_contour": "peaked",
        "emphasis": "throughout",
    },
    "...": {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "flat",
        "emphasis": "none",
    },
}

# ─── Capitalization cue mapping — PRD-026 §8.2 ───

CAPITALIZATION_CUE = {
    "primary_intent": "exclamation",
    "pace": "fast",
    "pitch_contour": "peaked",
    "emphasis": "throughout",
}

# ─── Lexical cue sets — PRD-026 §8.3 ───

HEDGING_PHRASES = ["maybe", "i guess", "sort of", "kind of"]
EMPHASIS_PHRASES = ["literally", "actually", "seriously"]
POLITENESS_PHRASES = ["please", "would you mind"]

# Deterministic lexical fallback priority: politeness > emphasis > hedging
LEXICAL_PRIORITY = ("politeness", "emphasis_cue", "hedging")

HEDGING_CUE = {
    "primary_intent": "statement",
    "pace": "slow",
    "pitch_contour": "rising",
    "emphasis": "none",
}

EMPHASIS_CUE = {
    "primary_intent": "statement",
    "pace": "moderate",
    "pitch_contour": "flat",
    "emphasis": "throughout",
}

# Politeness is a delivery cue only; it preserves the underlying sentence primary_intent.
POLITENESS_DELIVERY = {
    "pace": "moderate",
    "pitch_contour": "rising",
    "emphasis": "final_word",
}

# ─── Combination rules — PRD-026 §9 ───
# Key: (lexical_category, baseline_intent) or (cue_type, baseline_intent)

COMBINATION_RULES = {
    ("hedging", "question"): {
        "primary_intent": "question",
        "pace": "slow",
        "pitch_contour": "rising",
        "emphasis": "none",
    },
    ("uppercase", "exclamation"): {
        "primary_intent": "exclamation",
        "pace": "fast",
        "pitch_contour": "peaked",
        "emphasis": "throughout",
    },
    ("trailing_off", "statement"): {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "flat",
        "emphasis": "none",
    },
    ("emphasis_cue", "question"): {
        "primary_intent": "question",
        "pace": "moderate",
        "pitch_contour": "rising",
        "emphasis": "throughout",
    },
    ("politeness", "question"): {
        "primary_intent": "question",
        "pace": "moderate",
        "pitch_contour": "rising",
        "emphasis": "final_word",
    },
}


def _detect_baseline_intent(text: str) -> str:
    """Existing baseline: ? → question, ! → exclamation, else statement."""
    stripped = text.strip()
    if stripped.endswith("?"):
        return "question"
    elif stripped.endswith("!"):
        return "exclamation"
    return "statement"


def _detect_punctuation_cue(text: str) -> str | None:
    """Detect punctuation cues at the end of text."""
    stripped = text.strip()
    if stripped.endswith("?!"):
        return "?!"
    if stripped.endswith("!!!"):
        return "!!!"
    if stripped.endswith("..."):
        return "..."
    return None


def _detect_capitalization_cue(text: str) -> bool:
    """Detect deliberate uppercase emphasis.

    Considers it uppercase emphasis when the alphabetic characters are
    predominantly uppercase and the text has at least 2 alpha characters.
    This avoids triggering on single-letter words like "I".
    """
    stripped = text.strip()
    alpha_chars = [c for c in stripped if c.isalpha()]
    if len(alpha_chars) < 2:
        return False
    uppercase_count = sum(1 for c in alpha_chars if c.isupper())
    return uppercase_count == len(alpha_chars)


def _detect_all_lexical_cues(text: str) -> list[str]:
    """Detect all lexical cue categories present in text."""
    lower = text.lower()
    cues = []

    for phrase in POLITENESS_PHRASES:
        if phrase in lower:
            cues.append("politeness")
            break

    for phrase in EMPHASIS_PHRASES:
        if re.search(r'\b' + re.escape(phrase) + r'\b', lower):
            cues.append("emphasis_cue")
            break

    for phrase in HEDGING_PHRASES:
        if re.search(r'\b' + re.escape(phrase) + r'\b', lower):
            cues.append("hedging")
            break

    return cues


def _resolve_lexical_cue(text: str) -> str | None:
    """Detect and resolve lexical cues using explicit fixed priority ordering:
    politeness > emphasis > hedging.

    When multiple lexical cue categories are present in an utterance and no
    explicit combination rule exists for that exact combination, this fixed
    priority is used.
    """
    active_cues = set(_detect_all_lexical_cues(text))
    for category in LEXICAL_PRIORITY:
        if category in active_cues:
            return category
    return None


def detect_deterministic_cues(text: str) -> dict:
    """Detect all deterministic cues and resolve via combination rules and priority ordering.

    Priority order (PRD-026 §9):
        Explicit Tag (handled upstream in intent_pass)
            ↓
        Defined Combination Rule
            ↓
        Lexical Cue Priority (politeness > emphasis > hedging)
            ↓
        Punctuation / Capitalization Cue
            ↓
        Baseline Intent Fallback

    Returns:
        A dict with keys: primary_intent, pace, pitch_contour, emphasis.
    """
    baseline = _detect_baseline_intent(text)
    punct_cue = _detect_punctuation_cue(text)
    has_uppercase = _detect_capitalization_cue(text)
    lexical_cue = _resolve_lexical_cue(text)

    # Priority tier 1: Lexical cue combination rules
    # When a lexical cue is present, check its defined combination with the baseline first.
    if lexical_cue:
        combo_key = (lexical_cue, baseline)
        if combo_key in COMBINATION_RULES:
            return dict(COMBINATION_RULES[combo_key])

    # Priority tier 2: Lexical individual cues (resolved via politeness > emphasis > hedging)
    # When a lexical cue is present but no combination rule matches,
    # the lexical cue takes priority over punctuation/capitalization cues.
    if lexical_cue == "politeness":
        # Politeness modifies delivery only; underlying primary_intent is preserved
        return {
            "primary_intent": baseline,
            "pace": POLITENESS_DELIVERY["pace"],
            "pitch_contour": POLITENESS_DELIVERY["pitch_contour"],
            "emphasis": POLITENESS_DELIVERY["emphasis"],
        }
    elif lexical_cue == "emphasis_cue":
        return dict(EMPHASIS_CUE)
    elif lexical_cue == "hedging":
        return dict(HEDGING_CUE)

    # Priority tier 3: Capitalization and punctuation combination rules
    if has_uppercase:
        combo_key = ("uppercase", baseline)
        if combo_key in COMBINATION_RULES:
            return dict(COMBINATION_RULES[combo_key])
    if punct_cue == "...":
        combo_key = ("trailing_off", baseline)
        if combo_key in COMBINATION_RULES:
            return dict(COMBINATION_RULES[combo_key])

    # Priority tier 4: Individual punctuation cues
    if punct_cue and punct_cue in PUNCTUATION_CUES:
        return dict(PUNCTUATION_CUES[punct_cue])

    # Priority tier 5: Individual capitalization cue
    if has_uppercase:
        return dict(CAPITALIZATION_CUE)

    # Priority tier 6: Baseline fallback — PRD-026 §10
    baseline_mappings = {
        "question": {
            "primary_intent": "question",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        },
        "exclamation": {
            "primary_intent": "exclamation",
            "pace": "fast",
            "pitch_contour": "peaked",
            "emphasis": "throughout",
        },
        "statement": {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "flat",
            "emphasis": "none",
        },
    }
    return dict(baseline_mappings[baseline])
