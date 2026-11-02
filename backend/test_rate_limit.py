import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skip(reason="Requires a running local server")

def test_rate_limit():
    pass
