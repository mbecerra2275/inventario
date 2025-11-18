import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.database.connection import Base, get_db

# Crear nombre único por sesión
TEST_DB_NAME = f"inventario_test_{uuid.uuid4().hex[:8]}"

ENGINE_URL_ROOT = "mysql+pymysql://root:221175@localhost/"   # AJUSTAR usuario/pass aquí
ENGINE_URL_DB = f"{ENGINE_URL_ROOT}{TEST_DB_NAME}"

# Engine conectado a MySQL SIN base específica
root_engine = create_engine(ENGINE_URL_ROOT)
engine = create_engine(ENGINE_URL_DB)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Crear BD de test única
@pytest.fixture(scope="session", autouse=True)
def setup_database():

    # Crear BD
    with root_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME} CHARACTER SET utf8mb4;"))

    # Crear tablas
    Base.metadata.create_all(bind=engine)

    yield  # correr tests

    # Borrar BD al terminar
    with root_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME};"))


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_token():
    return "token.fake.test"
