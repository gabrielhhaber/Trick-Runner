"""
Speech subsystem via accessible_output2.
Auto selects the best available output: active screen reader first, SAPI fallback.
"""
from accessible_output2.outputs.auto import Auto

_speaker: Auto | None = None


def init_speech() -> None:
    global _speaker
    _speaker = Auto()


def speak(text: str, interrupt: bool = True) -> None:
    if _speaker is None:
        return
    try:
        _speaker.speak(text, interrupt=interrupt)
    except Exception:
        pass


def is_speaking() -> bool:
    """
    Return True while the current output is producing speech.

    - NVDA  : always returns False (by design) — the loop exits immediately.
    - Others: tries a generic is_speaking() method; falls back to False.
    """
    if _speaker is None:
        return False
    output = _speaker.get_first_available_output()
    if output is None:
        return False

    try:
        return bool(output.is_speaking())
    except Exception:
        pass

    return False
