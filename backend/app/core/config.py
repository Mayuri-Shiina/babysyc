import os
from dataclasses import dataclass, field
from pathlib import Path


# 从项目根目录或 backend 目录加载 .env 配置，并强制覆盖同名环境变量，避免本地旧变量干扰测试。
def load_environment_files() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    backend_root = Path(__file__).resolve().parents[2]
    env_values: dict[str, str] = {}

    for env_path in [repo_root / ".env", backend_root / ".env"]:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env_values[key.strip()] = value.strip().strip('"').strip("'")

    for key, value in env_values.items():
        os.environ[key] = value


# 将环境变量中的布尔值转换为 Python 布尔类型。
def parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


load_environment_files()


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Baby Growth Archive API"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "0.1.0"))
    debug: bool = field(default_factory=lambda: parse_bool(os.getenv("DEBUG"), True))
    api_v1_prefix: str = field(default_factory=lambda: os.getenv("API_V1_PREFIX", "/api/v1"))
    cors_allow_origins: list[str] = field(default_factory=lambda: ["*"])
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite+pysqlite:///./baby_growth.db"))
    ai_api_key: str = field(
        default_factory=lambda: os.getenv("ALI_BAILIAN_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    )
    ai_base_url: str = field(
        default_factory=lambda: os.getenv("ALI_BAILIAN_BASE_URL")
        or os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    )
    ai_model: str = field(
        default_factory=lambda: os.getenv("ALI_BAILIAN_MODEL") or os.getenv("OPENAI_MODEL", "qwen-omni-turbo-latest")
    )
    ai_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("AI_TIMEOUT_SECONDS", "60")))


settings = Settings()
