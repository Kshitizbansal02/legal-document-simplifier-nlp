import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest


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