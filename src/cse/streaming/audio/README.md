# Audio Streaming Pipeline

## Purpose

The **Audio Streaming Pipeline** provides the fundamental infrastructure for transporting synthesized audio through the Claire Speech Engine. It does **not** generate audio or handle actual playback/I/O (like PyAudio or WebSockets). 

Instead, it acts as the internal transport layer. By enforcing immutable `AudioFrame` structures and a thread-safe `StreamBuffer`, any acoustic backend can safely write frames to a stream, and any consumer (local audio device, file writer, network stream) can safely read from it.

## Core Components

- **`AudioFrame`**: An immutable dataclass representing a discrete chunk of PCM audio. It is PCM-format agnostic, keeping metadata like `sample_format` intact.
- **`AudioStream`**: A logical container holding an ordered sequence of `AudioFrame`s and associated stream metadata.
- **`StreamBuffer`**: A thread-safe, FIFO queue designed to handle both rapid low-latency chunks (e.g. streaming inference) and large batch chunks seamlessly. 
- **`StreamController`**: Manages the lifecycle of an `AudioStream` and coordinates the pushing/popping of frames into the `StreamBuffer`.
- **`StreamSerializer`**: Provides zero-cost abstraction for serializing/deserializing `AudioFrame`s to/from JSON over the wire (using base64-encoded bytes).

## Thread-Safety Model

The pipeline relies on a strict single-owner / multi-reader structure:
- **`StreamController`** must be owned by the thread producing the audio.
- **`StreamBuffer`** is thread-safe and acts as the boundary. The producer pushes frames, and any external consumer thread can safely pop frames from it.

## Example Usage

```python
from cse.streaming.audio import StreamController, AudioFrame

# 1. Initialize Controller
controller = StreamController(max_buffer_size=1000)
stream = controller.create_stream()

# 2. Producer pushes frames (usually from the AcousticBackend)
frame = AudioFrame(
    uuid=uuid.uuid4(),
    timestamp_ms=0.0,
    sample_rate=24000,
    channels=1,
    sample_format="PCM_16",
    samples=b"\x00\x00...",
    duration_ms=20.0
)
controller.push_frame(frame)

# 3. Consumer pops frames (e.g. your audio player loop)
popped_frame = controller.pop_frame(block_timeout=0.1)

# 4. Clean up
controller.close()
```
