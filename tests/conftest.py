import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models

# ===========================
# Настройка in-memory SQLite
# ===========================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===========================
# Переопределяем get_db для тестов
# ===========================
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ===========================
# Фикстура клиента
# ===========================
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# ===========================
# Фикстуры для создания объектов
# ===========================
@pytest.fixture
def create_test_user(db_session):
    def _create_user(name: str):
        user = models.User(name=name)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _create_user

@pytest.fixture
def create_test_character(db_session):
    def _create(name: str, user_id: int, level: int = 1, health: int = 100, exp: int = 0):
        character = models.Character(
            name=name,
            user_id=user_id,
            level=level,
            health=health,
            exp=exp
        )
        db_session.add(character)
        db_session.commit()
        db_session.refresh(character)
        return character
    return _create

@pytest.fixture
def create_test_item(db_session):
    def _create(name: str, character_id: int):
        item = models.Item(name=name, character_id=character_id)
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item
    return _create