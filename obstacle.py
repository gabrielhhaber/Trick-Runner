from __future__ import annotations
from enum import Enum
from sound_lib.stream import FileStream


class ObstacleType(Enum):
    PIT = "pit"
    BOULDER = "boulder"


class Obstacle:
    def __init__(self, position: int, obs_type: ObstacleType) -> None:
        self.position = position
        self.type = obs_type
        self.sound_stream: FileStream | None = None

    @property
    def sound_file(self) -> str:
        return "pit.ogg" if self.type == ObstacleType.PIT else "boulder.ogg"

    def check_collision(self, player) -> bool:
        """
        True when the player is at this obstacle's position and failed to
        perform the required action:
          - PIT     → must be jumping (up arrow pressed before arrival)
          - BOULDER → must be crouching (down arrow held)
        """
        if player.position != self.position:
            return False
        if self.type == ObstacleType.PIT:
            return not player.is_jumping
        return not player.is_crouching  # BOULDER
