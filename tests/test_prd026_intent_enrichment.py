"""PRD-026: Deterministic Intent Enrichment — Comprehensive Test Suite.

Tests cover all PRD-026 requirements per §15:
- valid tag parsing
- invalid tag parsing
- exact lowercase matching
- whitespace rejection
- one-tag limitation
- later literal bracket tags
- tag removal
- explicit-tag precedence
- explicit-tag performance mappings
- punctuation cues
- capitalization cues
- lexical cues
- cue combinations
- baseline fallback
- deterministic repeated execution
- all 10 canonical cases from §13
- PerformanceGraph schema verification (5 canonical fields only)
- PerformanceContext and intermediate pass tag propagation
"""
import pytest
from cse.performance.context import PerformanceContext
from cse.performance.passes.explicit_tag_parser import (
    parse_explicit_tag,
    get_explicit_tag_mapping,
    ExplicitTagError,
    VALID_TAGS,
    EXPLICIT_TAG_MAPPINGS,
)
from cse.performance.passes.deterministic_cues import detect_deterministic_cues
from cse.performance.passes.meaning import meaning_pass, MeaningResult
from cse.performance.passes.intent import intent_pass, IntentResult
from cse.performance.passes.planning import planning_pass, PerformancePlan
from cse.performance.graph import build_performance_graph, PerformanceGraph
from cse.performance.integration import execute_end_to_end
from cse.performance.translator import BaseTranslator


# ─── Helper: end-to-end graph extraction ───

class _GraphCapture(BaseTranslator):
    """Translator that captures the graph for assertion."""
    def translate(self, graph: PerformanceGraph) -> PerformanceGraph:
        return graph


def _run_pipeline(text: str) -> PerformanceGraph:
    """Run the full CPE pipeline and return the PerformanceGraph."""
    context = PerformanceContext(text=text)
    return execute_end_to_end(context, _GraphCapture())


# ═══════════════════════════════════════════════════════════════════════
# §5: Explicit Tag Parsing — Valid Tags
# ═══════════════════════════════════════════════════════════════════════

class TestExplicitTagParsingValid:

    @pytest.mark.parametrize("tag", sorted(VALID_TAGS))
    def test_valid_tag_parsed(self, tag):
        text = f"[{tag}] Hello world."
        parsed_tag, cleaned = parse_explicit_tag(text)
        assert parsed_tag == tag
        assert cleaned == "Hello world."

    def test_sarcastic_tag(self):
        tag, text = parse_explicit_tag("[sarcastic] Oh yeah, that's just great.")
        assert tag == "sarcastic"
        assert text == "Oh yeah, that's just great."

    def test_happy_tag(self):
        tag, text = parse_explicit_tag("[happy] What a beautiful day!")
        assert tag == "happy"
        assert text == "What a beautiful day!"


# ═══════════════════════════════════════════════════════════════════════
# §5: Explicit Tag Parsing — Invalid Tags
# ═══════════════════════════════════════════════════════════════════════

class TestExplicitTagParsingInvalid:

    def test_unknown_tag_raises_error(self):
        with pytest.raises(ExplicitTagError, match="Unknown tag"):
            parse_explicit_tag("[joyful] Hello!")

    def test_unknown_tag_excited(self):
        with pytest.raises(ExplicitTagError, match="Unknown tag"):
            parse_explicit_tag("[excited] Wow!")

    def test_uppercase_tag_rejected(self):
        with pytest.raises(ExplicitTagError, match="must be lowercase"):
            parse_explicit_tag("[Sarcastic] Oh yeah.")

    def test_all_caps_tag_rejected(self):
        with pytest.raises(ExplicitTagError, match="must be lowercase"):
            parse_explicit_tag("[SARCASTIC] Oh yeah.")

    def test_mixed_case_tag_rejected(self):
        with pytest.raises(ExplicitTagError, match="must be lowercase"):
            parse_explicit_tag("[Happy] Yay!")

    def test_whitespace_leading_rejected(self):
        with pytest.raises(ExplicitTagError, match="whitespace"):
            parse_explicit_tag("[ sarcastic] Oh yeah.")

    def test_whitespace_trailing_rejected(self):
        with pytest.raises(ExplicitTagError, match="whitespace"):
            parse_explicit_tag("[sarcastic ] Oh yeah.")

    def test_whitespace_both_rejected(self):
        with pytest.raises(ExplicitTagError, match="whitespace"):
            parse_explicit_tag("[ SARCASTIC ] Oh yeah.")

    def test_space_inside_tag_rejected(self):
        with pytest.raises(ExplicitTagError):
            parse_explicit_tag("[very happy] Yay!")

    def test_empty_tag_rejected(self):
        with pytest.raises(ExplicitTagError):
            parse_explicit_tag("[] Hello!")


# ═══════════════════════════════════════════════════════════════════════
# §5: One-Tag Rule
# ═══════════════════════════════════════════════════════════════════════

class TestOneTagRule:

    def test_no_tag_returns_none(self):
        tag, text = parse_explicit_tag("Hello there.")
        assert tag is None
        assert text == "Hello there."

    def test_later_bracket_tag_remains_literal(self):
        tag, text = parse_explicit_tag("[sarcastic] Oh [happy] yeah.")
        assert tag == "sarcastic"
        assert text == "Oh [happy] yeah."
        # The [happy] in the middle is literal text, not parsed

    def test_bracket_in_middle_not_parsed_as_tag(self):
        tag, text = parse_explicit_tag("Hello [happy] world.")
        assert tag is None
        assert text == "Hello [happy] world."


# ═══════════════════════════════════════════════════════════════════════
# §6: Tag Removal, Context Storage, and PerformanceGraph Schema
# ═══════════════════════════════════════════════════════════════════════

class TestTagRemovalAndStorage:

    def test_tag_removed_from_text(self):
        graph = _run_pipeline("[sarcastic] Oh yeah, that's just great.")
        assert graph.text == "Oh yeah, that's just great."

    def test_tag_stored_in_performance_context(self):
        tag, text = parse_explicit_tag("[sarcastic] Oh yeah, that's just great.")
        context = PerformanceContext(text=text, explicit_intent_overrides=tag)
        assert context.explicit_intent_overrides == "sarcastic"
        assert context.text == "Oh yeah, that's just great."

    def test_intermediate_passes_carry_explicit_intent_overrides(self):
        """Verify the explicit tag carries through context -> meaning -> intent -> planning."""
        tag, text = parse_explicit_tag("[sarcastic] Oh yeah.")
        context = PerformanceContext(text=text, explicit_intent_overrides=tag)
        assert context.explicit_intent_overrides == "sarcastic"

        meaning = meaning_pass(context)
        assert isinstance(meaning, MeaningResult)
        assert meaning.explicit_intent_overrides == "sarcastic"

        intent = intent_pass(meaning)
        assert isinstance(intent, IntentResult)
        assert intent.explicit_intent_overrides == "sarcastic"

        plan = planning_pass(intent)
        assert isinstance(plan, PerformancePlan)
        assert plan.explicit_intent_overrides == "sarcastic"

    def test_performance_graph_has_no_explicit_intent_overrides(self):
        """PRD-026: PerformanceGraph schema is not redesigned and does not contain explicit_intent_overrides."""
        graph = _run_pipeline("[sarcastic] Oh yeah, that's just great.")
        assert isinstance(graph, PerformanceGraph)
        assert set(graph.__dataclass_fields__.keys()) == {
            "text",
            "character_state",
            "semantics",
            "intent",
            "plan",
        }


# ═══════════════════════════════════════════════════════════════════════
# §6, §9: Explicit Tag Precedence
# ═══════════════════════════════════════════════════════════════════════

class TestExplicitTagPrecedence:

    def test_explicit_tag_overrides_question_punctuation(self):
        """Tag should override the ? punctuation baseline."""
        graph = _run_pipeline("[sad] Are you okay?")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"

    def test_explicit_tag_overrides_exclamation_punctuation(self):
        """Tag should override the ! punctuation baseline."""
        graph = _run_pipeline("[hesitant] Stop!")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"

    def test_explicit_tag_overrides_lexical_cues(self):
        """Tag should override hedging cue."""
        graph = _run_pipeline("[angry] Maybe you're right?")
        assert graph.intent["primary_intent"] == "exclamation"
        assert graph.plan["delivery"]["pace"] == "fast"

    def test_cue_detection_skipped_with_explicit_tag(self):
        """When explicit tag is present, deterministic cues should not affect output."""
        graph = _run_pipeline("[whisper] STOP!!!")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"
        assert graph.plan["delivery"]["emphasis"] == "none"


# ═══════════════════════════════════════════════════════════════════════
# §7: Explicit Tag Performance Mappings
# ═══════════════════════════════════════════════════════════════════════

class TestExplicitTagMappings:

    @pytest.mark.parametrize("tag,expected", [
        ("sarcastic", {"primary_intent": "statement", "pace": "slow", "pitch_contour": "flat", "emphasis": "final_word"}),
        ("happy", {"primary_intent": "exclamation", "pace": "fast", "pitch_contour": "rising", "emphasis": "throughout"}),
        ("angry", {"primary_intent": "exclamation", "pace": "fast", "pitch_contour": "peaked", "emphasis": "throughout"}),
        ("sad", {"primary_intent": "statement", "pace": "slow", "pitch_contour": "flat", "emphasis": "none"}),
        ("whisper", {"primary_intent": "statement", "pace": "slow", "pitch_contour": "flat", "emphasis": "none"}),
        ("hesitant", {"primary_intent": "statement", "pace": "slow", "pitch_contour": "rising", "emphasis": "none"}),
        ("emphatic", {"primary_intent": "statement", "pace": "fast", "pitch_contour": "peaked", "emphasis": "throughout"}),
    ])
    def test_tag_mapping_via_lookup(self, tag, expected):
        mapping = get_explicit_tag_mapping(tag)
        assert mapping == expected

    @pytest.mark.parametrize("tag", sorted(VALID_TAGS))
    def test_tag_mapping_through_pipeline(self, tag):
        graph = _run_pipeline(f"[{tag}] Test sentence.")
        expected = EXPLICIT_TAG_MAPPINGS[tag]
        assert graph.intent["primary_intent"] == expected["primary_intent"]
        assert graph.plan["delivery"]["pace"] == expected["pace"]
        assert graph.plan["delivery"]["pitch_contour"] == expected["pitch_contour"]
        assert graph.plan["delivery"]["emphasis"] == expected["emphasis"]


# ═══════════════════════════════════════════════════════════════════════
# §8.1: Punctuation Cues
# ═══════════════════════════════════════════════════════════════════════

class TestPunctuationCues:

    def test_interrobang_cue(self):
        result = detect_deterministic_cues("What are you doing?!")
        assert result["primary_intent"] == "exclamation"
        assert result["pace"] == "fast"
        assert result["pitch_contour"] == "peaked"
        assert result["emphasis"] == "throughout"

    def test_triple_exclamation_cue(self):
        result = detect_deterministic_cues("Wow!!!")
        assert result["primary_intent"] == "exclamation"
        assert result["pace"] == "fast"
        assert result["pitch_contour"] == "peaked"
        assert result["emphasis"] == "throughout"

    def test_ellipsis_cue(self):
        result = detect_deterministic_cues("I don't know...")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "slow"
        assert result["pitch_contour"] == "flat"
        assert result["emphasis"] == "none"

    def test_interrobang_through_pipeline(self):
        graph = _run_pipeline("What are you doing?!")
        assert graph.intent["primary_intent"] == "exclamation"
        assert graph.plan["delivery"]["pace"] == "fast"

    def test_ellipsis_through_pipeline(self):
        graph = _run_pipeline("I don't know...")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"


# ═══════════════════════════════════════════════════════════════════════
# §8.2: Capitalization Cue
# ═══════════════════════════════════════════════════════════════════════

class TestCapitalizationCue:

    def test_all_caps_exclamation(self):
        result = detect_deterministic_cues("STOP!")
        assert result["primary_intent"] == "exclamation"
        assert result["pace"] == "fast"
        assert result["pitch_contour"] == "peaked"
        assert result["emphasis"] == "throughout"

    def test_all_caps_no_punct(self):
        result = detect_deterministic_cues("STOP")
        assert result["primary_intent"] == "exclamation"
        assert result["pace"] == "fast"

    def test_normal_case_no_uppercase_cue(self):
        result = detect_deterministic_cues("Hello there.")
        assert result["primary_intent"] == "statement"

    def test_caps_through_pipeline(self):
        graph = _run_pipeline("STOP!")
        assert graph.intent["primary_intent"] == "exclamation"
        assert graph.plan["delivery"]["emphasis"] == "throughout"


# ═══════════════════════════════════════════════════════════════════════
# §8.3: Lexical Cues
# ═══════════════════════════════════════════════════════════════════════

class TestLexicalCues:

    # Hedging
    def test_hedging_maybe(self):
        result = detect_deterministic_cues("Maybe that's true.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "slow"
        assert result["pitch_contour"] == "rising"
        assert result["emphasis"] == "none"

    def test_hedging_i_guess(self):
        result = detect_deterministic_cues("I guess so.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "slow"

    def test_hedging_sort_of(self):
        result = detect_deterministic_cues("It's sort of like that.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "slow"

    def test_hedging_kind_of(self):
        result = detect_deterministic_cues("It's kind of nice.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "slow"

    # Emphasis
    def test_emphasis_literally(self):
        result = detect_deterministic_cues("I literally can't.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "moderate"
        assert result["pitch_contour"] == "flat"
        assert result["emphasis"] == "throughout"

    def test_emphasis_actually(self):
        result = detect_deterministic_cues("I actually like it.")
        assert result["primary_intent"] == "statement"
        assert result["emphasis"] == "throughout"

    def test_emphasis_seriously(self):
        result = detect_deterministic_cues("Seriously, stop.")
        assert result["primary_intent"] == "statement"
        assert result["emphasis"] == "throughout"

    # Politeness
    def test_politeness_please_statement(self):
        """Politeness on a statement must preserve statement intent."""
        result = detect_deterministic_cues("Please do not make that mistake again.")
        assert result["primary_intent"] == "statement"
        assert result["pace"] == "moderate"
        assert result["pitch_contour"] == "rising"
        assert result["emphasis"] == "final_word"

    def test_politeness_would_you_mind_question(self):
        """Politeness on a question must preserve question intent."""
        result = detect_deterministic_cues("Would you mind helping me?")
        assert result["primary_intent"] == "question"
        assert result["pace"] == "moderate"
        assert result["pitch_contour"] == "rising"
        assert result["emphasis"] == "final_word"


# ═══════════════════════════════════════════════════════════════════════
# §9: Cue Combination and Priority Rules
# ═══════════════════════════════════════════════════════════════════════

class TestCueCombinations:

    def test_hedging_plus_question(self):
        """hedging + question → question/slow/rising/none"""
        result = detect_deterministic_cues("I guess you're right?")
        assert result == {
            "primary_intent": "question",
            "pace": "slow",
            "pitch_contour": "rising",
            "emphasis": "none",
        }

    def test_uppercase_plus_exclamation(self):
        """uppercase + exclamation → exclamation/fast/peaked/throughout"""
        result = detect_deterministic_cues("STOP!!!")
        assert result == {
            "primary_intent": "exclamation",
            "pace": "fast",
            "pitch_contour": "peaked",
            "emphasis": "throughout",
        }

    def test_trailing_off_plus_statement(self):
        """trailing-off + statement → statement/slow/flat/none"""
        result = detect_deterministic_cues("I was thinking...")
        assert result == {
            "primary_intent": "statement",
            "pace": "slow",
            "pitch_contour": "flat",
            "emphasis": "none",
        }

    def test_emphasis_cue_plus_question(self):
        """emphasis cue + question → question/moderate/rising/throughout"""
        result = detect_deterministic_cues("Seriously, you're leaving?")
        assert result == {
            "primary_intent": "question",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "throughout",
        }

    def test_emphasis_throughout_preserved_in_question(self):
        """PRD-026: emphasis value MUST remain 'throughout' for emphasis + question."""
        result = detect_deterministic_cues("Seriously, you're leaving?")
        assert result["emphasis"] == "throughout"

    def test_politeness_plus_question(self):
        """politeness + question → question/moderate/rising/final_word"""
        result = detect_deterministic_cues("Would you mind helping me?")
        assert result == {
            "primary_intent": "question",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }


class TestLexicalOverPunctuationFallback:
    """When multiple cues are present and no explicit combination rule exists:
    lexical cues > punctuation/capitalization cues > baseline
    """

    def test_hedging_plus_trailing_off(self):
        """'Maybe you're right...' contains hedging ('maybe') and trailing-off ('...').
        No explicit combination rule for hedging+trailing-off exists.
        Lexical cue ('hedging') MUST take precedence over trailing-off.
        """
        result = detect_deterministic_cues("Maybe you're right...")
        assert result == {
            "primary_intent": "statement",
            "pace": "slow",
            "pitch_contour": "rising",
            "emphasis": "none",
        }

    def test_emphasis_plus_trailing_off(self):
        """'Actually, wait...' contains emphasis ('actually') and trailing-off ('...').
        Emphasis cue MUST take precedence over trailing-off.
        """
        result = detect_deterministic_cues("Actually, wait...")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "flat",
            "emphasis": "throughout",
        }

    def test_politeness_plus_trailing_off(self):
        """'Please wait...' contains politeness ('please') and trailing-off ('...').
        Politeness cue MUST take precedence over trailing-off, preserving statement intent.
        """
        result = detect_deterministic_cues("Please wait...")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }


class TestMultipleLexicalCuePriority:
    """When multiple lexical cue categories are present and no explicit combination rule exists:
    politeness > emphasis > hedging
    """

    def test_hedging_plus_emphasis_question(self):
        """'maybe seriously?' contains hedging ('maybe') and emphasis ('seriously').
        Priority: emphasis > hedging.
        Selected cue: emphasis.
        Combined with question baseline: emphasis + question combo rule applies.
        """
        result = detect_deterministic_cues("maybe seriously?")
        assert result == {
            "primary_intent": "question",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "throughout",
        }

    def test_hedging_plus_politeness_statement(self):
        """'maybe please do this.' contains hedging ('maybe') and politeness ('please').
        Priority: politeness > hedging.
        Selected cue: politeness.
        Politeness preserves statement intent and applies politeness delivery.
        """
        result = detect_deterministic_cues("maybe please do this.")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }

    def test_emphasis_plus_politeness_statement(self):
        """'seriously please do this.' contains emphasis ('seriously') and politeness ('please').
        Priority: politeness > emphasis.
        Selected cue: politeness.
        Politeness preserves statement intent and applies politeness delivery.
        """
        result = detect_deterministic_cues("seriously please do this.")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }

    def test_hedging_plus_emphasis_plus_politeness_statement(self):
        """'maybe seriously please do this.' contains hedging ('maybe'), emphasis ('seriously'), and politeness ('please').
        Priority: politeness > emphasis > hedging.
        Selected cue: politeness.
        Politeness preserves statement intent and applies politeness delivery.
        """
        result = detect_deterministic_cues("maybe seriously please do this.")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }


# ═══════════════════════════════════════════════════════════════════════
# §10: Baseline Fallback
# ═══════════════════════════════════════════════════════════════════════

class TestBaselineFallback:

    def test_question_baseline(self):
        result = detect_deterministic_cues("How are you?")
        assert result["primary_intent"] == "question"

    def test_exclamation_baseline(self):
        result = detect_deterministic_cues("Don't do that!")
        assert result["primary_intent"] == "exclamation"

    def test_statement_baseline(self):
        result = detect_deterministic_cues("I understand.")
        assert result["primary_intent"] == "statement"

    def test_question_baseline_full(self):
        result = detect_deterministic_cues("How are you?")
        assert result == {
            "primary_intent": "question",
            "pace": "moderate",
            "pitch_contour": "rising",
            "emphasis": "final_word",
        }

    def test_exclamation_baseline_full(self):
        result = detect_deterministic_cues("Don't do that!")
        assert result == {
            "primary_intent": "exclamation",
            "pace": "fast",
            "pitch_contour": "peaked",
            "emphasis": "throughout",
        }

    def test_statement_baseline_full(self):
        result = detect_deterministic_cues("I understand.")
        assert result == {
            "primary_intent": "statement",
            "pace": "moderate",
            "pitch_contour": "flat",
            "emphasis": "none",
        }


# ═══════════════════════════════════════════════════════════════════════
# §14: Deterministic Repeated Execution
# ═══════════════════════════════════════════════════════════════════════

class TestDeterministicExecution:

    def test_same_input_produces_same_output(self):
        """Identical input and context must produce identical Performance Graph output."""
        results = [_run_pipeline("Hello there.") for _ in range(10)]
        for r in results[1:]:
            assert r.text == results[0].text
            assert r.intent == results[0].intent
            assert r.plan == results[0].plan

    def test_explicit_tag_deterministic(self):
        results = [_run_pipeline("[sarcastic] Oh yeah, that's just great.") for _ in range(10)]
        for r in results[1:]:
            assert r.intent == results[0].intent
            assert r.plan == results[0].plan

    def test_cue_detection_deterministic(self):
        results = [_run_pipeline("I guess you're right?") for _ in range(10)]
        for r in results[1:]:
            assert r.intent == results[0].intent
            assert r.plan == results[0].plan


# ═══════════════════════════════════════════════════════════════════════
# §13: Canonical Test Cases (PRD-026 Cases 001–010)
# ═══════════════════════════════════════════════════════════════════════

class TestCanonicalCases:

    def test_case_001_plain_statement(self):
        """Case 001 — Plain Statement: Hello there."""
        graph = _run_pipeline("Hello there.")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "flat"
        assert graph.plan["delivery"]["emphasis"] == "none"

    def test_case_002_question(self):
        """Case 002 — Question: How are you?"""
        graph = _run_pipeline("How are you?")
        assert graph.intent["primary_intent"] == "question"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "final_word"

    def test_case_003_exclamation(self):
        """Case 003 — Exclamation: Don't do that!"""
        graph = _run_pipeline("Don't do that!")
        assert graph.intent["primary_intent"] == "exclamation"
        assert graph.plan["delivery"]["pace"] == "fast"
        assert graph.plan["delivery"]["pitch_contour"] == "peaked"
        assert graph.plan["delivery"]["emphasis"] == "throughout"

    def test_case_004_hesitation_hedging(self):
        """Case 004 — Hesitation / Hedging: Maybe you're right..."""
        graph = _run_pipeline("Maybe you're right...")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "none"

    def test_case_005_explicit_tag(self):
        """Case 005 — Explicit Tag: [sarcastic] Oh yeah, that's just great."""
        graph = _run_pipeline("[sarcastic] Oh yeah, that's just great.")
        assert graph.text == "Oh yeah, that's just great."
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "slow"
        assert graph.plan["delivery"]["pitch_contour"] == "flat"
        assert graph.plan["delivery"]["emphasis"] == "final_word"

    def test_case_006_hedging_plus_question(self):
        """Case 006 — Hedging + Question: I guess you're right?"""
        graph = _run_pipeline("I guess you're right?")
        assert graph.intent["primary_intent"] == "question"
        assert graph.plan["delivery"]["pace"] == "slow"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "none"

    def test_case_007_uppercase_plus_exclamation(self):
        """Case 007 — Uppercase + Exclamation: STOP!!!"""
        graph = _run_pipeline("STOP!!!")
        assert graph.intent["primary_intent"] == "exclamation"
        assert graph.plan["delivery"]["pace"] == "fast"
        assert graph.plan["delivery"]["pitch_contour"] == "peaked"
        assert graph.plan["delivery"]["emphasis"] == "throughout"

    def test_case_008_politeness_plus_question(self):
        """Case 008 — Politeness + Question: Would you mind helping me?"""
        graph = _run_pipeline("Would you mind helping me?")
        assert graph.intent["primary_intent"] == "question"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "final_word"

    def test_case_009_emphasis_plus_question(self):
        """Case 009 — Emphasis + Question: Seriously, you're leaving?"""
        graph = _run_pipeline("Seriously, you're leaving?")
        assert graph.intent["primary_intent"] == "question"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "throughout"

    def test_case_010_baseline_statement(self):
        """Case 010 — Baseline Statement: I understand."""
        graph = _run_pipeline("I understand.")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "flat"
        assert graph.plan["delivery"]["emphasis"] == "none"

    def test_politeness_statement_pipeline(self):
        """Politeness on a statement through full CPE pipeline: Please do not make that mistake again."""
        graph = _run_pipeline("Please do not make that mistake again.")
        assert graph.intent["primary_intent"] == "statement"
        assert graph.plan["delivery"]["pace"] == "moderate"
        assert graph.plan["delivery"]["pitch_contour"] == "rising"
        assert graph.plan["delivery"]["emphasis"] == "final_word"


# ═══════════════════════════════════════════════════════════════════════
# Error propagation: invalid tags through pipeline
# ═══════════════════════════════════════════════════════════════════════

class TestErrorPropagation:

    def test_unknown_tag_raises_through_pipeline(self):
        with pytest.raises(ExplicitTagError):
            _run_pipeline("[excited] Wow!")

    def test_uppercase_tag_raises_through_pipeline(self):
        with pytest.raises(ExplicitTagError):
            _run_pipeline("[Sarcastic] Oh yeah.")

    def test_whitespace_tag_raises_through_pipeline(self):
        with pytest.raises(ExplicitTagError):
            _run_pipeline("[ sarcastic] Oh yeah.")
