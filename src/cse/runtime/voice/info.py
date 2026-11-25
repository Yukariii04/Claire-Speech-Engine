"""Backend Voice Info (PRD-015 §10).

Lightweight representation of a voice provided by an acoustic backend,
as opposed to a VoicePackage loaded from disk.  Shares the same
VoiceMetadata dataclass so callers can read ``.metadata`` uniformly,
but does not carry a filesystem ``path`` and does not claim to be a
loadable package.
"""

from __future__ import annotations

from dataclasses import dataclass

from cse.voice.metadata import VoiceMetadata


@dataclass(frozen=True)
class BackendVoiceInfo:
    """Describes a voice that lives inside an acoustic backend.

    Unlike ``VoicePackage``, this type has no ``path`` attribute and
    never implies the voice was loaded from a package file on disk.
    ``metadata.license`` is ``None`` when the backend does not provide
    licensing information.
    """

    metadata: VoiceMetadata

