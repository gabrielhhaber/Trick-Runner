import os
import sys
from platform_utils.paths import module_path, is_frozen

if is_frozen():
    # When frozen by PyInstaller, DLLs live in lib/sound_lib/lib/ next to the exe,
    # not in sys._MEIPASS (the temp extraction dir used by embedded_data_path()).
    _exe_dir = os.path.dirname(sys.executable)
    x86_path = os.path.join(_exe_dir, 'lib', 'sound_lib', 'lib', 'x86')
    x64_path = os.path.join(_exe_dir, 'lib', 'sound_lib', 'lib', 'x64')
else:
    x86_path = os.path.join(module_path(), '..', 'lib', 'x86')
    x64_path = os.path.join(module_path(), '..', 'lib', 'x64')
