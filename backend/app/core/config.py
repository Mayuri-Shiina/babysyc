from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    app_name: str = "Baby Growth Archive API"
    app_version: str = "0.1.0"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_allow_origins: list[str] = field(default_factory=lambda: ["*"])


settings = Settings()
