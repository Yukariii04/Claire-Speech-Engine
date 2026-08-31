"""PRD-026: Explicit Performance Tag Parser.

Parses and validates [tag] prefix syntax from utterances.
Produces explicit_intent_overrides and strips the tag from text.
"""
import re

# Closed vocabulary — PRD-026 §5
VALID_TAGS = frozenset({
    "sarcastic",
    "happy",
    "angry",
    "sad",
    "whisper",
    "hesitant",
    "emphatic",
})

# Exact performance mappings — PRD-026 §7
EXPLICIT_TAG_MAPPINGS = {
    "sarcastic": {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "flat",
        "emphasis": "final_word",
    },
    "happy": {
        "primary_intent": "exclamation",
        "pace": "fast",
        "pitch_contour": "rising",
        "emphasis": "throughout",
    },
    "angry": {
        "primary_intent": "exclamation",
        "pace": "fast",
        "pitch_contour": "peaked",
        "emphasis": "throughout",
    },
    "sad": {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "flat",
        "emphasis": "none",
    },
    "whisper": {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "flat",
        "emphasis": "none",
    },
    "hesitant": {
        "primary_intent": "statement",
        "pace": "slow",
        "pitch_contour": "rising",
        "emphasis": "none",
    },
    "emphatic": {
        "primary_intent": "statement",
        "pace": "fast",
        "pitch_contour": "peaked",
        "emphasis": "throughout",
    },
}

# Pattern: opening bracket at start, capture content, closing bracket, then space + rest
_TAG_PATTERN = re.compile(r"^\[([^\]]*)\]\s*(.*)", re.DOTALL)


class ExplicitTagError(ValueError):
    """Raised when an explicit tag is invalid or unknown."""
    pass


def parse_explicit_tag(text: str) -> tuple[str | None, str]:
    """Parse an explicit [tag] prefix from the utterance.

    Returns:
        (tag, cleaned_text) where tag is None if no prefix tag is present,
        or the validated tag string if one is found. cleaned_text has the
        tag prefix removed.

    Raises:
        ExplicitTagError: If the tag syntax is present but the tag is
            invalid, unknown, or malformed.
    """
    match = _TAG_PATTERN.match(text)
    if match is None:
        return None, text

    raw_tag = match.group(1)
    rest = match.group(2)

    # Reject whitespace inside the tag
    if raw_tag != raw_tag.strip() or " " in raw_tag or "\t" in raw_tag:
        raise ExplicitTagError(
            f"Invalid tag syntax: whitespace inside tag is not allowed: [{raw_tag}]"
        )

    # Reject non-lowercase
    if raw_tag != raw_tag.lower():
        raise ExplicitTagError(
            f"Invalid tag: must be lowercase: [{raw_tag}]"
        )

    # Reject unknown tags (closed vocabulary)
    if raw_tag not in VALID_TAGS:
        raise ExplicitTagError(
            f"Unknown tag: [{raw_tag}]. Valid tags: {sorted(VALID_TAGS)}"
        )

    return raw_tag, rest


def get_explicit_tag_mapping(tag: str) -> dict:
    """Return the exact performance mapping for a validated explicit tag."""
    return dict(EXPLICIT_TAG_MAPPINGS[tag])
