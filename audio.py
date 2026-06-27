"""
Audio subsystem.
All playback goes through sound_lib.stream.FileStream (BASS backend).
pygame.mixer is intentionally not used.

One-shot sounds
---------------
In CPython, local variables are reference-counted: the moment play_oneshot()
returns, the FileStream object would be garbage-collected and __del__ would
call BASS_StreamFree() — killing the sound mid-play.
We keep all active one-shot streams in _oneshot_pool so they stay alive.
The pool is pruned lazily (before each new addition) to avoid growing forever.
"""
import os
from sound_lib.output import Output
from sound_lib.stream import FileStream
from constants import SOUNDS_DIR

_output: Output | None = None
_oneshot_pool: list[FileStream] = []   # keeps one-shot streams alive


def init_audio() -> None:
    global _output
    _output = Output()


def _path(filename: str) -> str:
    return os.path.join(SOUNDS_DIR, filename)


def play_sound(filename: str, pan: float = 0.0, volume: float = 1.0,
               loop: bool = False) -> FileStream:
    """
    Create, configure and play a FileStream.
    Caller owns the returned stream and must call free_stream() when done.
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
    Fire-and-forget playback.
    The stream is kept alive in _oneshot_pool until BASS reports it stopped.
    """
    global _oneshot_pool
    # Prune finished streams before adding a new one
    _oneshot_pool = [s for s in _oneshot_pool if s.is_playing]
    try:
        stream = FileStream(file=_path(filename))
        stream.pan = pan
        stream.volume = volume
        stream.play()
        _oneshot_pool.append(stream)
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
    global _output, _oneshot_pool
    _oneshot_pool.clear()
    if _output is not None:
        try:
            _output.free()
        except Exception:
            pass
        _output = None
