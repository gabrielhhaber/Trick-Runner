"""
Audio subsystem.
All playback goes through sound_lib.stream.FileStream (BASS backend).
pygame.mixer is intentionally not used.
"""
import os
from sound_lib.output import Output
from sound_lib.stream import FileStream
from constants import SOUNDS_DIR

_output: Output | None = None


def init_audio() -> None:
    global _output
    _output = Output()


def _path(filename: str) -> str:
    return os.path.join(SOUNDS_DIR, filename)


def play_sound(filename: str, pan: float = 0.0, volume: float = 1.0,
               loop: bool = False) -> FileStream:
    """
    Create, configure and play a FileStream.
    The caller owns the returned stream and is responsible for freeing it.
    """
    stream = FileStream(file=_path(filename))
    stream.pan = pan
    stream.volume = volume
    if loop:
        stream.looping = True
    stream.play()
    return stream


def play_oneshot(filename: str, pan: float = 0.0, volume: float = 1.0) -> None:
    """
    Fire-and-forget playback. BASS frees the channel automatically when done.
    """
    try:
        stream = FileStream(file=_path(filename), autofree=True)
        stream.pan = pan
        stream.volume = volume
        stream.play()
    except Exception:
        pass


def free_stream(stream: FileStream | None) -> None:
    """Stop and free a managed stream."""
    if stream is not None:
        try:
            stream.free()
        except Exception:
            pass


def cleanup_audio() -> None:
    global _output
    if _output is not None:
        try:
            _output.free()
        except Exception:
            pass
        _output = None
