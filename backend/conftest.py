import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def load_registry():
    """
    Load all models once before any test runs.
    autouse=True means this runs automatically for every test —
    no need to request it explicitly in test classes.
    """
    from dotenv import load_dotenv
    load_dotenv()
    from services.model_registry import registry
    asyncio.run(registry.load())
    yield
    registry.clear()


@pytest.fixture(scope="session")
def client(load_registry):
    """
    Single TestClient reused across all tests.
    Depends on load_registry so models are ready before any request.
    """
    from main import app
    with TestClient(app) as c:
        yield c