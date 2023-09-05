from typing import Any, Dict, List, Union

from pydantic import AnyHttpUrl, validator, Field
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_USER: str = Field("example-database", env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field("example-database-password", env='POSTGRES_PASSWORD')
    POSTGRES_SERVER: str = Field("postgres", env='POSTGRES_SERVER')  # this should match the service name in docker-compose
    POSTGRES_PORT: str = Field("5432", env='POSTGRES_PORT')  # standard Postgres port
    POSTGRES_DB: str = Field("example-database", env='POSTGRES_DB')

    def DATABASE_URL(self):
        return str(
            URL.create(
                drivername="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                database=self.POSTGRES_DB,
            )
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()