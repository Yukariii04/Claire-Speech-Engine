"""CAM-001 Local Deterministic Phonemizer (PRD-028 §6, §17).

Provides lightweight, local, deterministic text-to-phoneme conversion.
Does not require remote/cloud services.
"""

from __future__ import annotations

import os
import re
from typing import Sequence

from loguru import logger

# Canonical Symbol Vocabulary (256 tokens total)
# Special tokens
PAD = "<pad>"
UNK = "<unk>"
BOS = "<s>"
EOS = "</s>"
SPACE = " "

# Common IPA / eSpeak / English Phoneme Symbols
PUNCTUATION = list(" !'(),-.:;?\"")
IPA_VOWELS = [
    "i", "ɪ", "e", "ɛ", "æ", "a", "ɑ", "ɒ", "ɔ", "o", "ʊ", "u", "ʌ", "ə", "ɜ",
    "aɪ", "eɪ", "ɔɪ", "aʊ", "oʊ", "ɪə", "eə", "ʊə", "ɚ", "ɝ", "iː", "uː", "ɔː", "ɑː", "ɜː",
]
IPA_CONSONANTS = [
    "p", "b", "t", "d", "k", "ɡ", "g", "tʃ", "dʒ", "f", "v", "θ", "ð", "s", "z", "ʃ", "ʒ",
    "h", "m", "n", "ŋ", "l", "r", "w", "j", "ʔ", "ɾ", "ɹ", "ɬ", "ɮ",
]
LATIN_CHARS = [chr(c) for c in range(ord('a'), ord('z') + 1)]

# Assemble standard vocabulary table
_INITIAL_VOCAB = [PAD, UNK, BOS, EOS, SPACE] + PUNCTUATION + IPA_VOWELS + IPA_CONSONANTS + LATIN_CHARS
# Deduplicate preserving order
_SEEN = set()
VOCAB: list[str] = []
for tok in _INITIAL_VOCAB:
    if tok not in _SEEN:
        _SEEN.add(tok)
        VOCAB.append(tok)

# Pad remaining up to 256
while len(VOCAB) < 256:
    VOCAB.append(f"<res_{len(VOCAB)}>")

TOKEN_TO_ID: dict[str, int] = {tok: idx for idx, tok in enumerate(VOCAB)}
ID_TO_TOKEN: dict[int, str] = {idx: tok for idx, tok in enumerate(VOCAB)}
PAD_ID = TOKEN_TO_ID[PAD]
UNK_ID = TOKEN_TO_ID[UNK]
BOS_ID = TOKEN_TO_ID[BOS]
EOS_ID = TOKEN_TO_ID[EOS]


def _clean_text(text: str) -> str:
    """Normalize input text deterministically."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


class CAMPhonemizer:
    """Local, deterministic phonemizer for CAM-001."""

    def __init__(self, language: str = "en-us") -> None:
        self.language = language
        self._espeak_available: bool | None = None

    def _check_espeak(self) -> bool:
        """Check if eSpeak / phonemizer is functional locally."""
        if self._espeak_available is not None:
            return self._espeak_available

        try:
            import espeakng_loader
            import phonemizer.backend.espeak.wrapper
            lib_path = espeakng_loader.get_library_path()
            data_path = espeakng_loader.get_data_path()
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_library(lib_path)
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_data_path(data_path)
            os.environ["ESPEAK_DATA_PATH"] = data_path
        except Exception:
            pass

        try:
            from phonemizer import phonemize
            res = phonemize("test", language=self.language, backend="espeak", strip=True)
            self._espeak_available = bool(res)
        except Exception:
            self._espeak_available = False

        return self._espeak_available

    def text_to_phonemes(self, text: str) -> list[str]:
        """Convert text into a list of phoneme symbols deterministically."""
        cleaned = _clean_text(text)
        if not cleaned:
            return []

        if self._check_espeak():
            try:
                from phonemizer import phonemize
                phonemized = phonemize(
                    cleaned,
                    language=self.language,
                    backend="espeak",
                    strip=True,
                    preserve_punctuation=True,
                    with_stress=False,
                )
                # Tokenize phonemized string into symbols
                symbols: list[str] = []
                idx = 0
                while idx < len(phonemized):
                    matched = False
                    # Check 2-char tokens first
                    if idx + 2 <= len(phonemized) and phonemized[idx:idx+2] in TOKEN_TO_ID:
                        symbols.append(phonemized[idx:idx+2])
                        idx += 2
                        matched = True
                    elif phonemized[idx] in TOKEN_TO_ID:
                        symbols.append(phonemized[idx])
                        idx += 1
                        matched = True
                    else:
                        symbols.append(phonemized[idx].lower() if phonemized[idx].lower() in TOKEN_TO_ID else UNK)
                        idx += 1
                return symbols
            except Exception as e:
                logger.debug(f"eSpeak phonemization fallback: {e}")

        # Deterministic character / grapheme fallback
        symbols = []
        for char in cleaned.lower():
            if char in TOKEN_TO_ID:
                symbols.append(char)
            else:
                symbols.append(UNK)
        return symbols

    def phonemes_to_ids(self, phonemes: Sequence[str], add_bos_eos: bool = True) -> list[int]:
        """Map phoneme symbols to token IDs."""
        ids: list[int] = []
        if add_bos_eos:
            ids.append(BOS_ID)

        for sym in phonemes:
            ids.append(TOKEN_TO_ID.get(sym, UNK_ID))

        if add_bos_eos:
            ids.append(EOS_ID)

        return ids

    def text_to_ids(self, text: str, add_bos_eos: bool = True) -> list[int]:
        """Direct text-to-ID conversion."""
        phones = self.text_to_phonemes(text)
        return self.phonemes_to_ids(phones, add_bos_eos=add_bos_eos)

    def ids_to_phonemes(self, ids: Sequence[int]) -> list[str]:
        """Map token IDs back to phoneme symbols."""
        return [ID_TO_TOKEN.get(i, UNK) for i in ids]
