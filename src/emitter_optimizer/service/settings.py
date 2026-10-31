from ipaddress import IPv4Address

from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_HOST = IPv4Address("127.0.0.1")
DEFAULT_PORT = 8765


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMITTER_")

    host: IPv4Address = DEFAULT_HOST
    port: PositiveInt = DEFAULT_PORT
