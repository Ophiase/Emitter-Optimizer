from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_DIRECTORY = PROJECT_ROOT / "settings"

DEFAULT_EMITTER_FUNCTION = SETTINGS_DIRECTORY / "emitter.py"
DEFAULT_SENSOR_FUNCTION = SETTINGS_DIRECTORY / "sensor.py"
