# Claire Speech Engine — Example Scripts

Scaffolded by `cse example`. Each script is a standalone demo.

| File | Purpose | Python Requirement |
|------|---------|-------------------|
| example_styletts2.py | StyleTTS2 synthesis demo | Python 3.12+ |
| example_kokoro.py | Kokoro multi-voice demo | Python 3.12+ |

## Usage

```bash
# Run any script directly
python example_kokoro.py
python example_kokoro.py af_bella   # optional: pick a voice

# List all available voices first
cse voices
```

All scripts write `.wav` files into the current directory.
