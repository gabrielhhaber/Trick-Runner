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

# Per-level config: speed increases, map grows, obstacle count rises
LEVEL_CONFIGS = [
    {"step_interval": 400, "num_obstacles":  3, "map_length":  80},
    {"step_interval": 360, "num_obstacles":  5, "map_length": 100},
    {"step_interval": 310, "num_obstacles":  7, "map_length": 120},
    {"step_interval": 260, "num_obstacles":  9, "map_length": 140},
    {"step_interval": 210, "num_obstacles": 11, "map_length": 160},
    {"step_interval": 160, "num_obstacles": 13, "map_length": 180},
]
