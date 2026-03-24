from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import Base

engine = create_engine(settings.database_url, echo=settings.debug, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# 创建数据库表结构，后续启动阶段可按需要显式调用。
def create_database_tables() -> None:
    Base.metadata.create_all(bind=engine)


# 提供数据库会话依赖，后续接口接入真实 CRUD 时统一复用。
def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
