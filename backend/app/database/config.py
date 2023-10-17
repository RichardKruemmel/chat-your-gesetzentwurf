from typing import List, Union
from pydantic import AnyHttpUrl, validator, Field
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL
from dotenv import load_dotenv


load_dotenv()


class DatabaseSettings(BaseSettings):
    cors_origins: List[AnyHttpUrl] = []

    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    postgres_user: str = Field("example-database", env="POSTGRES_USER")
    postgres_password: str = Field("example-database-password", env="POSTGRES_PASSWORD")
    postgres_server: str = Field(
        "postgres", env="POSTGRES_SERVER"
    )  # this should match the service name in docker-compose
    postgres_port: str = Field("5432", env="POSTGRES_PORT")  # standard Postgres port
    postgres_db: str = Field("example-database", env="POSTGRES_DB")

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            database=self.postgres_db,
        )


database_settings = DatabaseSettings()
