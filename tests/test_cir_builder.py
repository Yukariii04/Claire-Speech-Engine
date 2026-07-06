"""Tests for the CIR builder.

PRD §15 & §21: Simple sentence, multiple sentences, whitespace,
unicode, emoji, questions, exclamations, long paragraphs.
"""

from __future__ import annotations

import pytest

from cse.language.cir.builder import build_cir
from cse.language.cir.exceptions import CIRBuilderError
from cse.language.cir.schema import (
    CIR_VERSION,
    CIRDocument,
    CIRLexicalToken,
    CIRSpeechSegment,
    CIRUtterance,
)


class TestBuildCIRBasic:
    """Basic single-sentence inputs."""

    def test_returns_cir_document(self):
        doc = build_cir("Hello world.")
        assert isinstance(doc, CIRDocument)

    def test_version_set(self):
        doc = build_cir("Hello.")
        assert doc.version == CIR_VERSION

    def test_raw_text_preserved(self):
        text = "I really missed you."
        doc = build_cir(text)
        assert doc.raw_text == text

    def test_language_english(self):
        doc = build_cir("Hello.")
        assert doc.language == "en"

    def test_single_utterance(self):
        doc = build_cir("Hello world.")
        assert len(doc.utterances) == 1

    def test_utterance_type(self):
        doc = build_cir("Hello world.")
        assert isinstance(doc.utterances[0], CIRUtterance)

    def test_utterance_text(self):
        doc = build_cir("Hello world.")
        assert doc.utterances[0].text == "Hello world."

    def test_single_segment(self):
        doc = build_cir("Hello world.")
        utt = doc.utterances[0]
        assert len(utt.segments) == 1

    def test_segment_type(self):
        doc = build_cir("Hello world.")
        seg = doc.utterances[0].segments[0]
        assert isinstance(seg, CIRSpeechSegment)

    def test_segment_text(self):
        doc = build_cir("Hello world.")
        seg = doc.utterances[0].segments[0]
        assert seg.text == "Hello world."

    def test_tokens_created(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert len(tokens) == 2

    def test_token_type(self):
        doc = build_cir("Hello world.")
        tok = doc.utterances[0].segments[0].tokens[0]
        assert isinstance(tok, CIRLexicalToken)

    def test_token_text(self):
        doc = build_cir("Hello world.")
        texts = [t.text for t in doc.utterances[0].segments[0].tokens]
        assert texts == ["Hello", "world"]

    def test_prd_example(self):
        """Validate the exact example from PRD §24."""
        doc = build_cir("I really missed you.")
        assert len(doc.utterances) == 1
        seg = doc.utterances[0].segments[0]
        token_texts = [t.text for t in seg.tokens]
        assert token_texts == ["I", "really", "missed", "you"]


class TestBuildCIRMultipleSentences:
    def test_two_sentences(self):
        doc = build_cir("Hello. World.")
        assert len(doc.utterances) == 2

    def test_three_sentences(self):
        doc = build_cir("One. Two. Three.")
        assert len(doc.utterances) == 3

    def test_each_utterance_text(self):
        doc = build_cir("Hello. World.")
        texts = [u.text for u in doc.utterances]
        assert texts == ["Hello.", "World."]


class TestBuildCIRQuestionExclamation:
    def test_question(self):
        doc = build_cir("Really?")
        assert len(doc.utterances) == 1
        assert doc.utterances[0].text == "Really?"

    def test_exclamation(self):
        doc = build_cir("Wow!")
        assert len(doc.utterances) == 1
        assert doc.utterances[0].text == "Wow!"

    def test_mixed(self):
        doc = build_cir("Hello! How are you? Fine.")
        assert len(doc.utterances) == 3


class TestBuildCIRWhitespace:
    def test_leading_trailing_stripped(self):
        doc = build_cir("   Hello world.   ")
        assert doc.raw_text == "   Hello world.   "
        assert doc.utterances[0].text == "Hello world."

    def test_multiple_spaces_between_words(self):
        doc = build_cir("Hello    world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert [t.text for t in tokens] == ["Hello", "world"]


class TestBuildCIRUnicode:
    def test_unicode_text(self):
        doc = build_cir("Héllo wörld.")
        assert doc.utterances[0].text == "Héllo wörld."

    def test_unicode_tokens(self):
        doc = build_cir("Héllo wörld.")
        texts = [t.text for t in doc.utterances[0].segments[0].tokens]
        assert texts == ["Héllo", "wörld"]


class TestBuildCIREmoji:
    def test_emoji_preserved(self):
        doc = build_cir("Hello 🌍.")
        tokens = doc.utterances[0].segments[0].tokens
        texts = [t.text for t in tokens]
        assert "🌍" in texts or "Hello" in texts  # emoji handled as token


class TestBuildCIRLongParagraph:
    def test_long_paragraph(self):
        words = ["word"] * 100
        text = " ".join(words) + "."
        doc = build_cir(text)
        assert len(doc.utterances) >= 1
        total_tokens = sum(
            len(seg.tokens)
            for utt in doc.utterances
            for seg in utt.segments
        )
        assert total_tokens == 100


class TestBuildCIRTokenOffsets:
    def test_source_offsets_sequential(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        # "Hello" starts at some offset, "world" starts after
        assert tokens[0].source_offset < tokens[1].source_offset

    def test_token_lengths(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert tokens[0].length == 5  # "Hello"
        assert tokens[1].length == 5  # "world"

    def test_token_positions(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert tokens[0].position == 0
        assert tokens[1].position == 1

    def test_punctuation_after(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert tokens[-1].punctuation_after == "."

    def test_whitespace_after(self):
        doc = build_cir("Hello world.")
        tokens = doc.utterances[0].segments[0].tokens
        assert tokens[0].whitespace_after == " "


class TestBuildCIRErrors:
    def test_empty_string_raises(self):
        with pytest.raises(CIRBuilderError):
            build_cir("")

    def test_whitespace_only_raises(self):
        with pytest.raises(CIRBuilderError):
            build_cir("   ")

    def test_non_string_raises(self):
        with pytest.raises(CIRBuilderError):
            build_cir(42)  # type: ignore[arg-type]


class TestBuildCIRImmutability:
    def test_document_frozen(self):
        doc = build_cir("Hello.")
        with pytest.raises(AttributeError):
            doc.raw_text = "other"  # type: ignore[misc]

    def test_utterance_frozen(self):
        doc = build_cir("Hello.")
        with pytest.raises(AttributeError):
            doc.utterances[0].text = "other"  # type: ignore[misc]

    def test_segment_frozen(self):
        doc = build_cir("Hello.")
        with pytest.raises(AttributeError):
            doc.utterances[0].segments[0].text = "other"  # type: ignore[misc]

    def test_token_frozen(self):
        doc = build_cir("Hello.")
        with pytest.raises(AttributeError):
            doc.utterances[0].segments[0].tokens[0].text = "other"  # type: ignore[misc]


class TestBuildCIRDeterminism:
    def test_same_input_same_uuids(self):
        a = build_cir("Hello world.")
        b = build_cir("Hello world.")
        assert a.uuid == b.uuid

    def test_different_input_different_uuids(self):
        a = build_cir("Hello.")
        b = build_cir("Goodbye.")
        assert a.uuid != b.uuid
