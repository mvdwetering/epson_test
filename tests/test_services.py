"""Test Epson services/actions."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
import pytest

from custom_components.epson_test.const import DOMAIN
from custom_components.epson_test.services import (
    SERVICE_SEND_RAW_COMMAND,
    async_setup_services,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_service_send_raw_command_returns_response(hass: HomeAssistant) -> None:
    """Test sending a raw command returns projector response."""
    async_setup_services(hass)

    mock_runtime_data = SimpleNamespace(send_command=AsyncMock(return_value="PWR=01"))
    mock_entry = SimpleNamespace(
        state=ConfigEntryState.LOADED,
        runtime_data=mock_runtime_data,
    )

    with patch.object(hass.config_entries, "async_get_entry", return_value=mock_entry):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEND_RAW_COMMAND,
            {"config_entry_id": "entry-id", "raw_command": "PWR?"},
            blocking=True,
            return_response=True,
        )

    assert response == {"response": "PWR=01"}
    mock_runtime_data.send_command.assert_awaited_once_with("PWR?")


async def test_service_send_raw_command_invalid_config_entry_id(
    hass: HomeAssistant,
) -> None:
    """Test sending raw command with unknown config entry id fails."""
    async_setup_services(hass)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEND_RAW_COMMAND,
            {"config_entry_id": "does_not_exist", "raw_command": "PWR?"},
            blocking=True,
            return_response=True,
        )
