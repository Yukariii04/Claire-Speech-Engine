# Claire Speech Engine CLI

A minimal, fast, and simple command-line interface for managing backends, voices, and generating speech.

## Usage

```bash
# Get help
cse help

# Check version
cse version

# List all available voices across all backends
cse voices

# Interactively select a default backend and voice
cse voice

# Check your currently selected backend and voice
cse voice current

# Manually set your default backend and voice
cse voice set kokoro af_heart

# Reset voice preferences to defaults
cse voice reset

# Generate speech (uses your saved default voice if --voice is omitted)
cse speak --voice af_heart --text "Hello world"
```
