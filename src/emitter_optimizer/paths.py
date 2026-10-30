from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_DIRECTORY = PROJECT_ROOT / "settings"
RESOURCES_DIRECTORY = PROJECT_ROOT / "resources"

DEFAULT_EMITTER_FUNCTION = SETTINGS_DIRECTORY / "emitter.py"
DEFAULT_SENSOR_FUNCTION = SETTINGS_DIRECTORY / "sensor.py"
DEFAULT_GUI_CONFIGURATION = SETTINGS_DIRECTORY / "gui.json"
DEFAULT_GUI_FONT = RESOURCES_DIRECTORY / "font" / "arial.ttf"
DEFAULT_SAVE_PATH = Path("save") / "emitters_positions.save"
