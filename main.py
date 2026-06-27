"""
Trick Runner — entry point.

State machine:
  menu  →  (start_game)  →  game
  game  →  (ESC / death) →  menu
"""
import sys
import pygame

from audio import init_audio, cleanup_audio
from speech import init_speech
from menu import Menu
from game_state import GameState


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((640, 120))
    pygame.display.set_caption("Trick Runner")

    init_audio()
    init_speech()

    state = Menu()
    clock = pygame.time.Clock()

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                _quit()

        result = state.handle_events(events)
        if result is None:
            result = state.update()

        if result == "quit":
            _quit()
        elif result == "start_game":
            state = GameState()
        elif result == "menu":
            pygame.event.clear()
            state = Menu()
            continue
        clock.tick(60)


def _quit() -> None:
    cleanup_audio()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
