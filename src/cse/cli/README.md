# Claire Speech Engine CLI

A minimal, fast, and simple command-line interface for managing models, voices, and generating speech.

## Usage

```bash
# Get help
cse help

# Check version
cse version

# Setup KittenTTS and pre-download models for offline access
cse setup

# List all available KittenTTS models
cse models

# Interactively select a default KittenTTS model
cse model

# Check currently selected model
cse model current

# Manually set default model
cse model set kitten-tts-micro-0.8

# Reset model preference to default
cse model reset

# Interactively select a default voice
cse voice

# Check your currently selected voice
cse voice current

# Manually set your default voice
cse voice set Bella

# Reset voice preferences to default
cse voice reset

# Copy runnable example scripts into the current directory
cse example
```
