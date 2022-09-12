from pydantic import BaseSettings

from decouple import config
from functools import lru_cache

class Settings(BaseSettings):
    """ Class that load all enviroment variable necessary to feature works"""

    def __new__(cls):
        cls.EVENT_PEOPLE_APP_NAME: str = config('RABBIT_EVENT_PEOPLE_APP_NAME')
        cls.EVENT_PEOPLE_TOPIC_NAME: str = config('RABBIT_EVENT_PEOPLE_TOPIC_NAME')
        cls.EVENT_PEOPLE_RABBIT_URL: str = config('RABBIT_URL')
        cls.EVENT_PEOPLE_VHOST: str = config('RABBIT_EVENT_PEOPLE_VHOST')
        return super().__new__(cls)


@lru_cache()
def get_settings() -> BaseSettings:  # pragma: no cover
    return Settings()
