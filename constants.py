import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 120
FPS = 60

TOTAL_LEVELS = 6
HEARING_RANGE = 15   # steps in each direction where obstacle sound is audible
JUMP_DURATION = 3    # how many steps the player stays airborne after jumping
MIN_OBSTACLE_GAP = 8 # minimum steps between two consecutive obstacles

# Per-level config: speed increases, map grows, obstacle count rises.
# map_length is sized so each obstacle gets ~13 usable steps in its segment
# (span = map_length - FIRST_POS(12) - END_MARGIN(6) ≈ num_obstacles * 13).
LEVEL_CONFIGS = [
    {"step_interval": 400, "num_obstacles":  5, "map_length":  83},
    {"step_interval": 360, "num_obstacles":  7, "map_length": 109},
    {"step_interval": 310, "num_obstacles":  9, "map_length": 135},
    {"step_interval": 260, "num_obstacles": 11, "map_length": 161},
    {"step_interval": 210, "num_obstacles": 13, "map_length": 187},
    {"step_interval": 160, "num_obstacles": 15, "map_length": 213},
]
