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
    if interrupt:
        try:
            _speaker.silence()
        except Exception:
            pass
    try:
        _speaker.speak(text)
    except Exception:
        pass
