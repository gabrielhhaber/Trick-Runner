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
    # Pass interrupt= to the underlying output (SAPI5 and JAWS both honour it).
    # Fall back to a plain call if the output doesn't accept the kwarg.
    try:
        _speaker.speak(text, interrupt=interrupt)
    except TypeError:
        try:
            _speaker.speak(text)
        except Exception:
            pass
    except Exception:
        pass


def is_speaking() -> bool:
    """
    Return True while the current output is producing speech.

    - JAWS  : queries IsJawsSpeaking() via COM.
    - SAPI5 : checks Status.RunningState (0 = idle, 1 = speaking, 2 = paused).
    - NVDA  : always returns False (by design) — the loop exits immediately.
    - Others: tries a generic is_speaking() method; falls back to False.
    """
    if _speaker is None:
        return False
    output = _speaker.get_first_available_output()
    if output is None:
        return False

    # Generic method (future-proof if accessible_output2 ever adds it)
    try:
        return bool(output.is_speaking())
    except AttributeError:
        pass

    # JAWS via COM
    try:
        return bool(output.object.IsJawsSpeaking())
    except Exception:
        pass

    # SAPI5 via voice status
    try:
        return output.object.Status.RunningState != 0
    except Exception:
        pass

    return False
