"""
Core game loop state.

The player runs automatically: every `step_interval` ms the engine advances
one position, plays a footstep sound, and checks for obstacle collisions.

Spatial audio
-------------
Each obstacle within HEARING_RANGE steps emits a looping sound with:

    pan    = clamp((obstacle_pos - player_pos) / HEARING_RANGE, -1.0, 1.0)
    volume = VOL_MAX - (VOL_MAX - VOL_MIN) * abs(distance) / HEARING_RANGE

  pan  > 0  →  right channel  (obstacle is ahead)
  pan  = 0  →  centre         (at the obstacle)
  pan  < 0  →  left channel   (obstacle is behind / passed)
  volume    →  rises linearly from VOL_MIN (edge of range) to VOL_MAX (at obstacle)

Both values are updated after every step.

Controls
--------
  UP arrow   : jump  (must be pressed before reaching a pit)
  DOWN arrow : crouch held  (must be held while at a boulder)
  C          : speak current position
  ESC        : return to main menu
"""
from __future__ import annotations

import sys
import pygame

from player import Player
from level import generate_level
from obstacle import Obstacle
from constants import HEARING_RANGE, TOTAL_LEVELS
from audio import play_sound, play_oneshot, free_stream
from speech import speak


class GameState:
    def __init__(self) -> None:
        self._font = pygame.font.SysFont(None, 26)
        self._current_level = 0
        self.player: Player = Player()          # replaced in _load_level
        self.obstacles: list[Obstacle] = []
        self._step_interval = 400
        self._map_length = 80
        self._last_step_ms = 0
        self._load_level()

    # ------------------------------------------------------------------
    # Level management
    # ------------------------------------------------------------------

    def _load_level(self) -> None:
        self._stop_all_obstacle_sounds()
        self.obstacles, self._step_interval, self._map_length = generate_level(
            self._current_level
        )
        self.player = Player()
        self._last_step_ms = pygame.time.get_ticks()
        speak(f"Nível {self._current_level + 1}. Boa sorte!")

    def _stop_all_obstacle_sounds(self) -> None:
        for obs in self.obstacles:
            if obs.sound_stream is not None:
                free_stream(obs.sound_stream)
                obs.sound_stream = None

    # ------------------------------------------------------------------
    # Spatial audio update
    # ------------------------------------------------------------------

    _VOL_MIN = 0.15   # volume at the edge of hearing range
    _VOL_MAX = 1.00   # volume when player is right at the obstacle

    def _spatial(self, distance: int) -> tuple[float, float]:
        """Return (pan, volume) for a given signed distance to an obstacle."""
        ratio = abs(distance) / HEARING_RANGE          # 0.0 (closest) → 1.0 (edge)
        pan = max(-1.0, min(1.0, distance / HEARING_RANGE))
        volume = self._VOL_MAX - (self._VOL_MAX - self._VOL_MIN) * ratio
        return pan, volume

    def _update_obstacle_sounds(self) -> None:
        """Refresh pan + volume; start or stop streams as obstacles enter/leave range."""
        for obs in self.obstacles:
            distance = obs.position - self.player.position  # + = ahead, − = behind
            if abs(distance) <= HEARING_RANGE:
                pan, volume = self._spatial(distance)
                if obs.sound_stream is None:
                    obs.sound_stream = play_sound(
                        obs.sound_file, pan=pan, volume=volume, loop=True
                    )
                else:
                    try:
                        obs.sound_stream.pan = pan
                        obs.sound_stream.volume = volume
                    except Exception:
                        pass
            else:
                if obs.sound_stream is not None:
                    free_stream(obs.sound_stream)
                    obs.sound_stream = None

    # ------------------------------------------------------------------
    # State interface
    # ------------------------------------------------------------------

    def handle_events(self, events: list) -> str | None:
        keys = pygame.key.get_pressed()

        # Crouch is a held key — track transitions to avoid repeating the sound
        if keys[pygame.K_DOWN]:
            if self.player.start_crouch():
                play_oneshot("crouch.ogg")
        else:
            if self.player.stand_up():
                play_oneshot("standup.ogg")

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_UP:
                if self.player.jump():
                    play_oneshot("jump.ogg")

            elif event.key == pygame.K_c:
                speak(f"Posição {self.player.position} de {self._map_length}.")

            elif event.key == pygame.K_ESCAPE:
                self._stop_all_obstacle_sounds()
                return "menu"

        return None

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self._last_step_ms >= self._step_interval:
            self._last_step_ms = now
            self._do_step()

    def _do_step(self) -> None:
        self.player.step()
        play_oneshot("step.ogg")

        # Collision check before updating spatial audio
        for obs in self.obstacles:
            if obs.check_collision(self.player):
                self._handle_death(obs)
                return

        self._update_obstacle_sounds()

        if self.player.position >= self._map_length:
            self._handle_level_complete()

    # ------------------------------------------------------------------
    # Death / level-complete
    # ------------------------------------------------------------------

    def _handle_death(self, obs: Obstacle) -> None:
        self._stop_all_obstacle_sounds()
        play_oneshot(obs.sound_file, pan=0.0, volume=1.0)
        pygame.time.wait(1500)
        speak("Você morreu!")
        pygame.time.wait(2500)
        pygame.quit()
        sys.exit()

    def _handle_level_complete(self) -> None:
        self._stop_all_obstacle_sounds()
        play_oneshot("levelup.ogg")
        self._current_level += 1

        if self._current_level >= TOTAL_LEVELS:
            speak("Parabéns! Você completou todos os níveis do Trick Runner!")
            pygame.time.wait(4000)
            pygame.quit()
            sys.exit()

        speak(f"Nível completo! Preparando nível {self._current_level + 1}.")
        pygame.time.wait(1800)
        self._load_level()

    # ------------------------------------------------------------------
    # Visual feedback (debug overlay — game is primarily audio)
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((8, 8, 24))

        state_label = (
            "Pulando"   if self.player.is_jumping  else
            "Agachado"  if self.player.is_crouching else
            "Correndo"
        )
        info = self._font.render(
            f"Nível {self._current_level + 1}  |  "
            f"Pos: {self.player.position}/{self._map_length}  |  "
            f"{state_label}",
            True, (200, 220, 255),
        )
        screen.blit(info, (10, 8))

        obs_summary = "  ".join(
            f"{'P' if o.type.value == 'pit' else 'B'}@{o.position}"
            for o in self.obstacles
        )
        obs_surf = self._font.render(f"Obs: {obs_summary}", True, (120, 130, 140))
        screen.blit(obs_surf, (10, 38))

        speed_surf = self._font.render(
            f"Intervalo: {self._step_interval}ms", True, (90, 110, 90)
        )
        screen.blit(speed_surf, (10, 68))
