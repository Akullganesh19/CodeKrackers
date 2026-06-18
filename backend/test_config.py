import os
import pytest
from pydantic import ValidationError

def test_settings_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    # We must patch the environment before the module is imported.
    # Since pytest might have already imported it, we can test the class manually.

    import sys
    if "backend.core.config" in sys.modules:
        del sys.modules["backend.core.config"]

    with pytest.raises(ValidationError) as exc_info:
        from backend.core.config import Settings
        # Import itself might trigger initialization: settings = Settings()

    assert "SECRET_KEY" in str(exc_info.value) or "Field required" in str(exc_info.value)

def test_settings_accepts_secret_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    import sys
    if "backend.core.config" in sys.modules:
        del sys.modules["backend.core.config"]

    from backend.core.config import Settings

    settings = Settings()
    assert settings.SECRET_KEY == "test-secret-key"
