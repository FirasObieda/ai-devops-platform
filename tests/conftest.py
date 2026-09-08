import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, getDb

testEngine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=testEngine,
)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=testEngine)

    db = TestSessionLocal()

    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        db.commit()
    finally:
        db.close()

    def overrideGetDb():
        testDb = TestSessionLocal()

        try:
            yield testDb
        finally:
            testDb.close()

    app.dependency_overrides[getDb] = overrideGetDb

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=testEngine)
