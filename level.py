"""
Level map generator.

Obstacle positions are randomised each game session (no fixed seed).

Fairness rules
--------------
- MIN_OBSTACLE_GAP (8 steps) is enforced between every pair of consecutive
  obstacles regardless of type.
- After a PIT specifically, an extra POST_PIT_BUFFER is added on top of the
  base gap: the player is airborne for JUMP_DURATION steps after jumping, so
  the next obstacle must be placed after they can safely land AND have at
  least REACTION_STEPS additional steps to hear and react.

  worst-case landing offset = JUMP_DURATION - 1  (pressed UP one step before
  the pit → airborne for JUMP_DURATION steps → lands JUMP_DURATION-1 steps
  after the pit)

  total minimum gap after a pit  = (JUMP_DURATION - 1) + REACTION_STEPS
                                  = 2 + 6 = 8  (== MIN_OBSTACLE_GAP, so the
  base gap already covers this, but we make it explicit here so changing any
  constant stays consistent)
"""
import random
from obstacle import Obstacle, ObstacleType
from constants import LEVEL_CONFIGS, MIN_OBSTACLE_GAP, JUMP_DURATION

REACTION_STEPS = 6      # minimum steps the player needs to hear & respond
POST_PIT_BUFFER = max(0, (JUMP_DURATION - 1) + REACTION_STEPS - MIN_OBSTACLE_GAP)


def generate_level(level_index: int) -> tuple[list[Obstacle], int, int]:
    """
    Returns (obstacles, step_interval_ms, map_length) for the given level.
    level_index is 0-based.
    Layout is randomised on every call.
    """
    config = LEVEL_CONFIGS[level_index]
    num_obstacles: int = config["num_obstacles"]
    step_interval: int = config["step_interval"]
    map_length: int = config["map_length"]

    rng = random.Random()   # seeded from system entropy → different each run

    obstacles: list[Obstacle] = []
    pos = 14                # clear opening stretch so the player can get ready
    end = map_length - 6   # leave a short safe stretch at the end

    prev_type: ObstacleType | None = None

    while len(obstacles) < num_obstacles and pos < end:
        obs_type = rng.choice([ObstacleType.PIT, ObstacleType.BOULDER])
        obstacles.append(Obstacle(pos, obs_type))

        # Base random gap
        gap = rng.randint(MIN_OBSTACLE_GAP, MIN_OBSTACLE_GAP + 6)

        # Extra buffer when the obstacle we just placed is a pit, so the
        # player cannot land from the jump and immediately collide.
        if obs_type == ObstacleType.PIT:
            gap += POST_PIT_BUFFER

        pos += gap
        prev_type = obs_type

    return obstacles, step_interval, map_length
