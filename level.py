"""
Level map generator.

Distribution strategy
---------------------
The usable map range [FIRST_POS, last_pos) is divided into `num_obstacles`
equal segments. One obstacle is placed randomly inside each segment, subject
to a minimum gap from the previous obstacle. This guarantees even coverage
of the whole map regardless of the number of obstacles or map length.

Fairness: MIN_OBSTACLE_GAP (8 steps) ensures the player has time to land
from a jump and react to the next obstacle before reaching it.
"""
import random
from obstacle import Obstacle, ObstacleType
from constants import LEVEL_CONFIGS, MIN_OBSTACLE_GAP

_FIRST_POS = 12   # clear opening run so the player can get ready
_END_MARGIN = 6   # safe landing strip at the finish


def generate_level(level_index: int) -> tuple[list[Obstacle], int, int]:
    """
    Returns (obstacles, step_interval_ms, map_length) for the given level.
    level_index is 0-based.
    Layout is randomised on every call (system-entropy seed).
    """
    config = LEVEL_CONFIGS[level_index]
    num_obstacles: int = config["num_obstacles"]
    step_interval: int = config["step_interval"]
    map_length: int    = config["map_length"]

    rng = random.Random()

    first = _FIRST_POS
    last  = map_length - _END_MARGIN   # exclusive upper bound
    span  = last - first               # usable steps

    segment = span / num_obstacles     # width of each equal slice (float)

    obstacles: list[Obstacle] = []
    prev_pos = first - MIN_OBSTACLE_GAP  # sentinel — allows first obstacle at `first`

    for i in range(num_obstacles):
        seg_start = first + int(i * segment)
        seg_end   = first + int((i + 1) * segment) - 1  # inclusive

        # Enforce minimum gap from the previous obstacle
        earliest = max(seg_start, prev_pos + MIN_OBSTACLE_GAP)
        latest   = min(seg_end, last - 1)

        if earliest > latest:
            # Segment fully consumed by the gap constraint — skip this slot
            continue

        pos      = rng.randint(earliest, latest)
        obs_type = rng.choice([ObstacleType.PIT, ObstacleType.BOULDER])
        obstacles.append(Obstacle(pos, obs_type))
        prev_pos = pos

    return obstacles, step_interval, map_length
