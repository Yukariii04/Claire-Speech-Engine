# Fish Speech Backend

The `fishspeech` backend connects The Claire Speech Engine to the powerful [Fish Speech](https://github.com/fishaudio/fish-speech) zero-shot voice cloning model.

This backend uses a subprocess adapter to connect to the raw Fish Speech v1.5 Python CLI tools for VQ encoding, semantic code generation, and acoustic decoding.

## Zero-Shot Voice Discovery

Fish Speech doesn't have hardcoded voices. Instead, it clones voices dynamically from reference `.wav` files.

To make this seamless, the `FishSpeechBackend` features **Dynamic Recursive Voice Discovery**.

### How to add a voice:
1. Obtain a `.wav` file containing clean, isolated speech of the voice you want to clone.
2. Drop that `.wav` file **literally anywhere** in your project directory (in the root, in a `voices/` folder, or 4 folders deep—it doesn't matter).
3. The name of the file becomes the Voice ID. (e.g. `my_awesome_voice.wav` becomes the voice `my_awesome_voice`).

When you run `cse voices`, the backend will recursively scan your entire workspace, automatically skip junk directories (like `.git`, `venv`, `temp`), and register every `.wav` file it finds.

When you synthesize speech using that voice, CSE automatically grabs the `.wav` file from wherever you hid it and uses it as the zero-shot cloning reference audio.

## Configuration

You can override the directories the backend uses via environment variables if you are running inference on a cloud machine (like Google Colab):

- `FISH_SPEECH_DIR`: Path to the cloned fish-speech repo (default: `/content/fish-speech`)
- `FISH_CHECKPOINT_DIR`: Path to downloaded weights (default: `/content/checkpoints/fish-speech-1.5`)
- `VOICES_DIR`: If set, forces the backend to *only* scan this directory for `.wav` files instead of scanning the whole workspace.
