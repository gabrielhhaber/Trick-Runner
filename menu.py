"""
Main menu state.

Navigation: UP / DOWN arrows (wrap-around).
Confirm   : ENTER  →  returns "start_game" or "quit".
Cancel    : ESC    →  returns "quit".

Sounds    : menu_nav.ogg on navigation, menu_select.ogg on selection.
Speech    : full option description spoken on every focus change.
"""
import pygame
from audio import play_oneshot
from speech import speak

_OPTIONS = [
    {
        "label": "Iniciar Jogo",
        "spoken": (
            "Iniciar jogo: pressione a seta para cima para saltar, "
            "mantenha pressionada a seta para baixo para abaixar-se, "
            "pressione C para ver suas coordenadas."
        ),
        "action": "start_game",
    },
    {
        "label": "Sair",
        "spoken": "Sair.",
        "action": "quit",
    },
]


class Menu:
    def __init__(self) -> None:
        self._selected = 0
        self._first_update = True
        self._font = pygame.font.SysFont(None, 38)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _announce(self) -> None:
        speak(_OPTIONS[self._selected]["spoken"])
        play_oneshot("menu_nav.ogg")

    # ------------------------------------------------------------------
    # State interface (same contract as GameState)
    # ------------------------------------------------------------------

    def update(self) -> None:
        if self._first_update:
            self._first_update = False
            self._announce()

    def handle_events(self, events: list) -> str | None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_UP:
                self._selected = (self._selected - 1) % len(_OPTIONS)
                self._announce()

            elif event.key == pygame.K_DOWN:
                self._selected = (self._selected + 1) % len(_OPTIONS)
                self._announce()

            elif event.key == pygame.K_RETURN:
                play_oneshot("menu_select.ogg")
                return _OPTIONS[self._selected]["action"]

            elif event.key == pygame.K_ESCAPE:
                return "quit"

        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        for i, option in enumerate(_OPTIONS):
            color = (255, 220, 0) if i == self._selected else (170, 170, 170)
            surf = self._font.render(option["label"], True, color)
            screen.blit(surf, (24, 18 + i * 50))
