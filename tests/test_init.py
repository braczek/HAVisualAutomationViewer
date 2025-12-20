"""Unit tests for the __init__.py module."""

import logging
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock homeassistant and its submodules
mock_ha = MagicMock()
sys.modules["homeassistant"] = mock_ha
sys.modules["homeassistant.config_entries"] = mock_ha.config_entries = MagicMock()
sys.modules["homeassistant.const"] = mock_ha.const = MagicMock()
sys.modules["homeassistant.core"] = mock_ha.core = MagicMock()
sys.modules["homeassistant.helpers"] = mock_ha.helpers = MagicMock()
sys.modules["homeassistant.helpers.config_validation"] = (
    mock_ha.helpers.config_validation
) = MagicMock()
sys.modules["homeassistant.helpers.typing"] = mock_ha.helpers.typing = MagicMock()
sys.modules["homeassistant.components"] = mock_ha.components = MagicMock()
sys.modules["homeassistant.components.http"] = mock_ha.components.http = MagicMock()

# Mock the api module
mock_api = MagicMock()
mock_api.setup_api = AsyncMock()
sys.modules["custom_components.visualautoview.api"] = mock_api

from custom_components.visualautoview import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.visualautoview.const import DOMAIN


class TestAsyncSetup:
    """Tests for async_setup function."""

    @pytest.fixture
    def mock_hass(self):
        """Mock HomeAssistant."""
        hass = MagicMock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_config(self):
        """Mock config."""
        return {}

    @pytest.mark.asyncio
    async def test_async_setup_success(self, mock_hass, mock_config, caplog):
        """Test successful setup."""
        mock_api.setup_api.return_value = True
        with caplog.at_level(logging.DEBUG):
            result = await async_setup(mock_hass, mock_config)
        assert result is True
        assert DOMAIN in mock_hass.data
        mock_api.setup_api.assert_called_once_with(mock_hass)
        assert "Setting up Visual AutoView integration" in caplog.text

    @pytest.mark.asyncio
    async def test_async_setup_api_failure(self, mock_hass, mock_config, caplog):
        """Test setup with API failure."""
        mock_api.setup_api.return_value = False
        with caplog.at_level(logging.WARNING):
            result = await async_setup(mock_hass, mock_config)
        assert result is True
        assert "Failed to setup Visual AutoView API" in caplog.text


class TestAsyncSetupEntry:
    """Tests for async_setup_entry function."""

    @pytest.fixture
    def mock_hass(self):
        """Mock HomeAssistant."""
        hass = MagicMock()
        hass.data = {DOMAIN: {}}
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        return hass

    @pytest.fixture
    def mock_entry(self):
        """Mock ConfigEntry."""
        entry = MagicMock()
        entry.entry_id = "test_entry"
        return entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(self, mock_hass, mock_entry, caplog):
        """Test successful entry setup."""
        with caplog.at_level(logging.DEBUG):
            result = await async_setup_entry(mock_hass, mock_entry)
        assert result is True
        assert mock_entry.entry_id in mock_hass.data[DOMAIN]
        assert mock_hass.data[DOMAIN][mock_entry.entry_id]["config_entry"] == mock_entry
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once_with(
            mock_entry, []
        )
        assert (
            f"Setting up Visual AutoView config entry: {mock_entry.entry_id}"
            in caplog.text
        )


class TestAsyncUnloadEntry:
    """Tests for async_unload_entry function."""

    @pytest.fixture
    def mock_hass(self):
        """Mock HomeAssistant."""
        hass = MagicMock()
        hass.data = {DOMAIN: {"test_entry": {"config_entry": MagicMock()}}}
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        return hass

    @pytest.fixture
    def mock_entry(self):
        """Mock ConfigEntry."""
        entry = MagicMock()
        entry.entry_id = "test_entry"
        return entry

    @pytest.mark.asyncio
    async def test_async_unload_entry_success(self, mock_hass, mock_entry, caplog):
        """Test successful entry unload."""
        with caplog.at_level(logging.DEBUG):
            result = await async_unload_entry(mock_hass, mock_entry)
        assert result is True
        mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
            mock_entry, []
        )
        assert mock_entry.entry_id not in mock_hass.data[DOMAIN]
        assert (
            f"Unloading Visual AutoView config entry: {mock_entry.entry_id}"
            in caplog.text
        )

    @pytest.mark.asyncio
    async def test_async_unload_entry_failure(self, mock_hass, mock_entry):
        """Test unload failure."""
        mock_hass.config_entries.async_unload_platforms.return_value = False
        result = await async_unload_entry(mock_hass, mock_entry)
        assert result is False
        assert mock_entry.entry_id in mock_hass.data[DOMAIN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
