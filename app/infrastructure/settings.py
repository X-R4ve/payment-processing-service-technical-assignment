from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, \
    YamlConfigSettingsSource, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str
    port: int = Field(5432, ge=1, le=65535)
    user: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return (f'postgresql+asyncpg://{self.user}:{self.password}'
                f'@{self.host}:{self.port}/{self.name}')


class RabbitMQSettings(BaseModel):
    host: str
    port: int = Field(5672, ge=1, le=65535)
    user: str
    password: str
    vhost: str = '%2f'

    @property
    def url(self, secure: bool = True):
        return (f'amqp://{self.user}:{self.password}'
                f'@{self.host}:{self.port}/{self.vhost}')



class Settings(BaseSettings):
    db: DatabaseSettings
    rabbitmq: RabbitMQSettings
    api_key: str

    model_config = SettingsConfigDict(
        yaml_file='/etc/payment_processing_service/settings.yaml'
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


@lru_cache
def get_settings() -> Settings:
    return Settings()

get_settings()
