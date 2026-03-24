from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core import database
from app.main import app
from app.models import Base


# 为测试创建独立 SQLite 引擎和会话工厂，避免污染本地开发数据库。
@pytest.fixture()
def test_db_session_factory(tmp_path: Path) -> sessionmaker:
    test_db_path = tmp_path / "test_baby_growth.db"
    test_engine = create_engine(
        f"sqlite+pysqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=test_engine)
    factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    database.engine = test_engine
    database.SessionLocal = factory
    return factory


# 提供测试客户端，并将数据库依赖切换为临时测试数据库。
@pytest.fixture()
def client(test_db_session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    def override_get_db_session() -> Generator[Session, None, None]:
        session = test_db_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
