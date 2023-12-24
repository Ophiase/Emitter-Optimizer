import os
import json

dn = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def _compose_path(*args) -> str:
    return os.path.join(dn, *args)

def _read_json(filename: str) -> dict:
    with open(_compose_path(filename), 'r') as file:
        data = json.load(file)
    return data

DEFAULT_EMITTER_FUNCTION: str = _compose_path("settings", "emitter.py")
DEFAULT_SENSOR_FUNCTION: str = _compose_path("settings", "sensor.py")

DEFAULT_GUI_JSON: dict = _read_json(_compose_path("settings", "gui.json"))
DEFAULT_GUI_FONT: str = _compose_path("resources", "font", "arial.ttf")