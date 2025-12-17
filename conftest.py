"""Configuration for pytest."""

import pytest
import sys
from pathlib import Path

# Add custom_components to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
