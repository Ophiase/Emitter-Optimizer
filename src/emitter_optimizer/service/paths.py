from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INSTALLED_DATA = Path(__file__).resolve().parents[1] / "data"
DATA_ROOT = INSTALLED_DATA if INSTALLED_DATA.is_dir() else PROJECT_ROOT
SETTINGS_DIRECTORY = DATA_ROOT / "settings"
RESOURCES_DIRECTORY = DATA_ROOT / "resources"

DEFAULT_EMITTER_FUNCTION = SETTINGS_DIRECTORY / "emitter.py"
DEFAULT_SENSOR_FUNCTION = SETTINGS_DIRECTORY / "sensor.py"
DEFAULT_GUI_CONFIGURATION = SETTINGS_DIRECTORY / "gui.json"
DEFAULT_GUI_FONT = RESOURCES_DIRECTORY / "font" / "arial.ttf"
DEFAULT_SAVE_PATH = PROJECT_ROOT / "out" / "positions.csv"
