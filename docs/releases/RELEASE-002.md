All four refinements are solid, and the architectural one is the most important catch yet — the score theater aside, the substance holds up. My read on each, then the updated doc:

1. **Download trigger too early** — correct, and it exposes something worth being consistent about: the StyleTTS2 backend you already have *already* does this right — its `_ensure_model()` is called lazily from inside `synthesize()`, not from `initialize()`. So the fix isn't "invent a new pattern," it's "make FishSpeech and Kokoro match the pattern StyleTTS2 already uses." I'll standardize on that rather than introducing yet another trigger point (like `load_voice()`), so all three backends behave identically.

2. **Richer `cse backends` output** — agree, cheap, adopting the dashboard format as specified.

3. **`def main()` + `if __name__ == "__main__"`** — agree, trivial, standard practice.

4. **README table** — agree, adding it.

5. **Don't hardcode implementation details as requirements** — good instinct for a spec that shouldn't go stale, but worth one pushback: some of those specifics (the exact checkpoint filename, the `am_fable`/`am_fenrir` correction) are things I only caught *by actually verifying against the source*, and stripping them out entirely would mean Antigravity re-derives them from scratch and could reintroduce the same class of bug. I've kept the formal requirement abstract (SHALL language) as recommended, but kept a parenthetical pointing at today's known-correct source for context — not as a locked-in requirement, just so the verification work already done doesn't get thrown away.

6. **`cse doctor`** — good idea, correctly scoped to *not* go in this release. I've added it to the roadmap note at the end only.

```
################################################################################
#                     THE CLAIRE SPEECH ENGINE (CSE)
#
# Release Engineering Checklist
#
# Release : v1.0.4
# Version : 1.0.4
#
################################################################################
````

# Objective

Make FishSpeech, StyleTTS2, and Kokoro consistently self-sufficient (asset
checks deferred to first synthesis, not backend load), ship default voices
for FishSpeech and StyleTTS2, expand Kokoro to its full official voice set,
and add a `cse example`/`cse backends` developer toolkit.

This is a packaging + release milestone.

No other framework features shall be added beyond what's listed below.

---

# 1. Implementation Changes (Required Before Packaging)

## 1a. Backend self-sufficiency — deferred, not eager
- `load_backend()` / `initialize()` SHALL NOT trigger any download or
  heavy asset check. Loading a backend only prepares it to be used.
- Each backend SHALL ensure its required runtime assets are available
  before synthesis, and only at that point — the check (and download, if
  needed) happens on first `synthesize()` call, not on `load_backend()`
  and not on `load_voice()`. The acquisition mechanism is backend-specific
  (downloading, extracting, validating, or locating existing assets) and
  shall remain fully encapsulated within the backend.
- StyleTTS2 already does this correctly today (`_ensure_model()` is
  called from `synthesize()`) — bring FishSpeech and Kokoro in line with
  that same pattern rather than introducing a different trigger point,
  so behavior is consistent across all three backends.
- Whatever the mechanism, it SHALL be visible (progress indication,
  logged destination path) rather than silent, and SHALL raise a clear,
  actionable error if acquisition fails or a dependency is missing —
  this already exists in FishSpeech today and should be preserved.
- (Currently, for implementer reference only, not a locked requirement:
  FishSpeech pulls its checkpoint from `fishaudio/fish-speech-1.5` via
  `huggingface_hub`, verifying `firefly-gan-vq-fsq-8x1024-21hz-generator.pth`,
  matching COLAB-001; Kokoro pulls `kokoro-v1.0.onnx` + `voices-v1.0.bin`
  from the `kokoro-onnx` GitHub release, also matching COLAB-001;
  StyleTTS2 relies on the package's own first-use download. If any of
  these sources change, this document should not need to be updated —
  only the backend's internal implementation.)

## 1b. FishSpeech default voice
- Move `claire_neutral.wav` from the repo root into
  `src/cse/backends/fishspeech/assets/claire_neutral.wav`, packaged via
  `package_data`/`MANIFEST.in`.
- Keep the existing whole-project `os.walk()` auto-discovery in
  `_scan_for_wavs()` unchanged.
- Always merge the packaged `claire_neutral` asset into `voices_map` as a
  baseline entry, so at least one voice exists even with an empty scan.
  A project-level wav with the same voice_id overrides the packaged one.
- Replace the "grab whichever wav came first" fallback with an explicit
  fallback to `claire_neutral`, logging a warning naming both the
  requested and fallback voice. If the packaged asset itself is missing,
  raise a clear error.

## 1c. StyleTTS2 default voice + thread safety
- Reuse the same `claire_neutral.wav` asset (or a StyleTTS2-specific
  copy, Antigravity's judgment) as the default reference.
- In `synthesize()`, pass the resolved reference path to
  `self._tts.inference(...)` via its `target_voice_path` argument instead
  of calling it with text only — verify the exact keyword name against
  the actually-installed `styletts2` package version before wiring it in.
- `load_voice()` should accept an explicit path or the bundled default;
  `list_voices()` should report `claire_neutral` instead of the current
  generic `"default"` entry.
- Wrap the `torch.load` monkeypatch in `_ensure_model()` with a
  module-level `threading.Lock()` so two concurrent first-loads can't
  race. Keep the existing `if self._tts is not None: return`
  short-circuit outside the lock's hot path. Add a code comment noting
  the accepted limitation: while the lock is held, any other code in the
  process calling `torch.load` also sees `weights_only=False`, since
  `torch.load` is process-global and `styletts2` doesn't expose the flag.

## 1d. Kokoro full voice set
- Replace the current 28-voice, English-only `list_voices()` with the
  full official voice set from `hexgrad/Kokoro-82M` — verify directly
  against `VOICES.md` in that repo at implementation time rather than
  copying a list from a secondary source, since at least one entry in
  the current list (`am_fable`, which should be `am_fenrir`) is already
  wrong for exactly that reason.
- Add the additional languages: Spanish (`ef_`/`em_`), French (`ff_`),
  Hindi (`hf_`/`hm_`), Italian (`if_`/`im_`), Japanese (`jf_`/`jm_`),
  Portuguese (`pf_`/`pm_`), Mandarin (`zf_`/`zm_`).
- Update `BackendCapabilities.supported_languages` from `("en",)` to the
  full set of language codes now covered.
- Verify whether Japanese and Mandarin voices need an additional optional
  G2P dependency beyond what `kokoro-onnx` installs by default — if so,
  document it and raise a clear error naming the missing extra rather
  than producing garbled audio.

---

# 2. New: Developer Toolkit Commands

## 2a. `cse example`
- Bundled templates in `src/cse/_scaffold/`:
  - `example_fishspeech.py`
  - `example_styletts2.py`
  - `example_kokoro.py`
  - `README.md`, including a table:

    | File | Purpose |
    |------|---------|
    | example_fishspeech.py | Fish Speech demo |
    | example_styletts2.py | StyleTTS2 demo |
    | example_kokoro.py | Kokoro demo |

  Packaged via `package_data` so they ship inside the wheel.
- `cse example` copies all 3 scripts + README into the current directory.
- `cse example fishspeech` / `cse example styletts2` / `cse example
  kokoro` copies just that one script (+ README).
- Do not overwrite existing files with the same name without `--force`.
- Print a short confirmation listing what was copied and where.

## 2b. Script content — teaching only, no infrastructure logic
Since asset handling now lives entirely in the backends (1a), each script
stays minimal, following standard Python structure:

```python
from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("fishspeech")
    engine.load_voice()

    while True:
        text = input("Text to speak (empty to quit): ").strip()
        if not text:
            break
        result = engine.speak(text)
        print(f"Saved: {result.audio_path}")


if __name__ == "__main__":
    main()
```

- No manual checkpoint-download code, no manual dependency checks — if
  something's missing, the backend itself raises a clear error (per 1a),
  and the script just lets that error surface.
- Output wav filenames increment in the current directory
  (`fishspeech_out_1.wav`, `fishspeech_out_2.wav`, ...).
- Kokoro script should let the user optionally pass a voice id, defaulting
  to `af_heart`, and print a short note that `cse voices` lists all
  available options.

## 2c. `cse backends` — health dashboard
Richer than a checklist — a short status report per backend, e.g.:

```
Installed Backends

FishSpeech
  Status         : Ready
  Models         : Installed
  Default Voice  : claire_neutral
  Version        : 1.5
────────────────────────
Kokoro
  Status         : Ready
  Models         : Installed
  Voices         : 53
────────────────────────
StyleTTS2
  Status         : Missing Dependency
  Reason         : styletts2 not installed
  Install        : pip install styletts2
```

Pairs with the existing `cse voices` as the two discovery commands.

---

# 3. Packaging Review

Verify

- `pyproject.toml` package_data includes both the FishSpeech/StyleTTS2
  voice assets and the new `_scaffold/` directory
- `cse example` and `cse backends` are registered and callable
  immediately after install
- version bump (1.0.2 → 1.0.4)
- no new hard runtime dependencies

---

# 4. Build Verification

```bash
python -m build
unzip -l dist/*.whl | grep -E "claire_neutral|_scaffold"
```

Confirm both the voice assets and all 4 scaffold files are actually
inside the wheel.

---

# 5. Twine Validation

```bash
twine check dist/*
```

---

# 6. Local Install Dry Run (No TestPyPI This Release)

From a clean venv, in an **empty, unrelated directory**:

```bash
python -m venv /tmp/cse_release_check
source /tmp/cse_release_check/bin/activate
pip install dist/*.whl
cse backends
cse example
ls   # expect: example_fishspeech.py, example_styletts2.py, example_kokoro.py, README.md
python -c "from cse import SpeechEngine; e = SpeechEngine(); e.load_backend('fishspeech'); print('backend loaded, no download yet'); e.load_voice(); print(e.speak('Testing the default voice.'))"
```

Confirm no download happens until the `speak()` call — this is the
specific behavior the self-sufficiency fix targets. This is the only
pre-publish safety net since there's no TestPyPI stage — don't skip it.

---

# 7. PyPI

Publish directly to PyPI.

---

# 8. Fresh Environment Validation (Post-Publish)

Clean environment, empty directory, install from the real index:

```bash
pip install claire-speech-engine
cse backends
cse example
python example_fishspeech.py
python example_styletts2.py
python example_kokoro.py
```

Confirm all three run end-to-end from a bare install with no source repo
present, with model acquisition happening automatically and visibly
inside the backend on first `speak()` — not eagerly at `load_backend()`
— and each producing a playable wav in the current directory.

---

# 9. COLAB-001

Verify Fish Speech, StyleTTS2, and Kokoro all still generate audio via
`pip install claire-speech-engine`, and confirm the bundled default
voices load correctly for FishSpeech and StyleTTS2.

---

# 10. Rollback Plan

If Section 8 fails after publishing: yank the release (PyPI doesn't allow
overwriting a version), fix, bump to the next patch, re-run from Section 4.

---

# 11. GitHub Release

Release Notes covering:
- Backend self-sufficiency: asset checks deferred to first `speak()`,
  consistent across all three backends
- Bundled default voice for FishSpeech and StyleTTS2
- Deterministic fallback (FishSpeech no longer picks an arbitrary wav)
- Thread-safe StyleTTS2 model loading
- Full Kokoro voice set (all languages, `am_fable` → `am_fenrir` fix)
- New `cse example` and `cse backends` commands

---

# 12. Documentation

Update README:
- Quickstart: mention `cse example` and `cse backends` right after install
- FishSpeech/StyleTTS2: document the bundled default voice
- Kokoro: document the full voice list and any language-specific extras
- New section: "Local example scripts" pointing at the scaffold README

---

# 13. Acceptance Criteria

Release complete when

✓ Package builds, wheel contains voice assets + all scaffold files
✓ Twine passes
✓ Local wheel dry run (Section 6) passes from an empty directory, with
  no download triggered until `speak()`
✓ PyPI passes
✓ `cse example` on a fresh install produces all 3 scripts + README
✓ `cse backends` reports the full status dashboard per backend
✓ Each of the 3 scripts runs standalone end-to-end and writes a wav into
  the current directory
✓ FishSpeech and StyleTTS2 both default to `claire_neutral` with no
  silent wrong-voice fallback
✓ Kokoro exposes the full corrected voice list across all languages
✓ Two concurrent StyleTTS2 first-loads don't corrupt `torch.load` for a
  third caller
✓ COLAB-001 works using PyPI
✓ GitHub Release published

################################################################################

END OF RELEASE-002

################################################################################

---

# AI Instructions

Do not modify CIR, PerformanceTimeline, Runtime, or the public `SpeechEngine` API.

Asset acquisition is triggered by first `synthesize()` call, matching the
existing StyleTTS2 pattern — not by `load_backend()` or `load_voice()`.
Do not duplicate acquisition logic in the example scripts.

Verify the Kokoro voice list against `hexgrad/Kokoro-82M`'s `VOICES.md`
directly rather than trusting any secondary source.

Verify the reference-voice keyword argument against the actually-installed
`styletts2` package version before wiring it in.

There is no TestPyPI stage. Section 6's local wheel install is the only
pre-publish validation — do not skip it.

AFTER IMPLEMENTATION

1. Bring FishSpeech and Kokoro's asset handling in line with StyleTTS2's
   existing lazy, first-synthesize pattern.
2. Implement default voices (FishSpeech + StyleTTS2), the StyleTTS2 lock,
   and the corrected full Kokoro voice list.
3. Implement `cse example` (with per-backend targeting), `cse backends`
   dashboard output, and the three minimal teaching scripts.
4. Build the wheel and verify all new assets are actually included.
5. Run the local clean-venv dry run from an empty directory, confirming
   no download happens before `speak()`.
6. Publish directly to PyPI.
7. Immediately validate with a fresh install + `cse example` + `cse
   backends` from the real PyPI index.
8. Re-run COLAB-001 against the new release.
9. Send the updated repository ZIP, release notes, and the final
   COLAB-001 notebook for review.

REVIEW WILL VERIFY

• Packaging (all new assets actually in the wheel)
• Deferred, consistent backend self-sufficiency (no eager downloads)
• Default-voice + deterministic-fallback behavior (FishSpeech, StyleTTS2)
• StyleTTS2 concurrency lock
• Full, corrected Kokoro voice list
• `cse example` + `cse backends` + all 3 scripts running standalone
• Real PyPI installation, post-publish
• GitHub release
• Notebook reproducibility
• Documentation updates

COMMIT MESSAGE

feat: deferred backend self-sufficiency, default voices, full Kokoro set, cse example/backends

TAG

v1.0.4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# 🚀 After RELEASE-002

```text
v1.0.2 (current PyPI)
        │
        ▼
RELEASE-002
(deferred self-sufficiency + default voices + full Kokoro set + dev toolkit)
        │
        ▼
v1.0.4
        │
        ▼
Local wheel dry run
        │
        ▼
PyPI (direct)
        │
        ▼
COLAB-001
        │
        ▼
Framework Complete — Developer-Ready SDK
        │
        ▼
Roadmap: cse doctor (diagnostic command, next quality-of-life release)
        │
        ▼
CPE-000
Claire Performance Engine Architecture
```