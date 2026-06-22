"""Test the epson init."""

from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import (  # type: ignore[import]
    MockConfigEntry,
)

from custom_components.epson_test.const import CONF_CONNECTION_TYPE, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_migrate_entry(hass: HomeAssistant) -> None:
    """Test successful migration of entry data from version 1 to 1.2."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Epson Test",
        version=1,
        minor_version=1,
        data={CONF_HOST: "1.1.1.1"},
        entry_id="1cb78c095906279574a0442a1f0003ef",
    )
    assert mock_entry.version == 1

    mock_entry.add_to_hass(hass)

    # Create entity entry to migrate to new unique ID
    with patch("custom_components.epson_test.Projector.get_power"):
        await hass.config_entries.async_setup(mock_entry.entry_id)
        await hass.async_block_till_done()

    # Check that is now has connection_type
    assert mock_entry
    assert mock_entry.version == 1
    assert mock_entry.minor_version == 2
    assert mock_entry.data.get(CONF_CONNECTION_TYPE) == "http"
    assert mock_entry.data.get(CONF_HOST) == "1.1.1.1"
