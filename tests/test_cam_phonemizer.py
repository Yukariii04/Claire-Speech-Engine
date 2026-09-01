"""Tests for CAM-001 Local Deterministic Phonemizer (PRD-028 §6, §17)."""

import pytest

from cse.acoustic.cam.phonemizer import (
    BOS_ID,
    CAMPhonemizer,
    EOS_ID,
    ID_TO_TOKEN,
    PAD_ID,
    TOKEN_TO_ID,
    UNK_ID,
    VOCAB,
)


@pytest.fixture
def phonemizer():
    return CAMPhonemizer()


class TestCAMPhonemizer:
    def test_vocab_size_is_256(self):
        assert len(VOCAB) == 256
        assert len(TOKEN_TO_ID) == 256
        assert len(ID_TO_TOKEN) == 256

    def test_special_tokens_defined(self):
        assert PAD_ID == 0
        assert UNK_ID == 1
        assert BOS_ID == 2
        assert EOS_ID == 3

    def test_text_to_phonemes_deterministic(self, phonemizer):
        text = "The quick brown fox jumps over the lazy dog."
        phones1 = phonemizer.text_to_phonemes(text)
        phones2 = phonemizer.text_to_phonemes(text)
        assert phones1 == phones2
        assert len(phones1) > 0

    def test_text_to_ids_includes_bos_eos(self, phonemizer):
        text = "Hello world."
        ids = phonemizer.text_to_ids(text, add_bos_eos=True)
        assert ids[0] == BOS_ID
        assert ids[-1] == EOS_ID
        assert len(ids) >= 4

    def test_text_to_ids_without_bos_eos(self, phonemizer):
        text = "Hello world."
        ids = phonemizer.text_to_ids(text, add_bos_eos=False)
        assert ids[0] != BOS_ID
        assert ids[-1] != EOS_ID

    def test_roundtrip_conversion(self, phonemizer):
        text = "Speech test."
        phones = phonemizer.text_to_phonemes(text)
        ids = phonemizer.phonemes_to_ids(phones, add_bos_eos=False)
        recovered_phones = phonemizer.ids_to_phonemes(ids)
        assert recovered_phones == phones

    def test_empty_string_handling(self, phonemizer):
        assert phonemizer.text_to_phonemes("") == []
        assert phonemizer.text_to_ids("", add_bos_eos=False) == []
