"""Test the epson config flow."""

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.epson_test.const import CONF_CONNECTION_TYPE, DOMAIN, HTTP, SERIAL
from custom_components.epson_test.exceptions import CannotConnect, PoweredOff

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    with patch("custom_components.epson_test.config_flow.validate_projector"):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}
    assert result["step_id"] == config_entries.SOURCE_USER
    with (
        patch(
            "custom_components.epson_test.config_flow.validate_projector",
            side_effect=[
                SimpleNamespace(close=lambda: None),
                SimpleNamespace(
                    close=lambda: None,
                    get_serial_number_alt=AsyncMock(return_value="12345"),
                ),
            ],
        ),
        patch(
            "custom_components.epson_test.async_setup_entry",
            return_value=True,
        ),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "1.1.1.1", CONF_PORT: "8080", CONF_CONNECTION_TYPE: HTTP},
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Epson Projector"
    assert result2["data"] == {CONF_CONNECTION_TYPE: HTTP, CONF_HOST: "1.1.1.1", CONF_PORT: "8080"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.epson_test.config_flow.validate_projector",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "1.1.1.1"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_powered_off(hass: HomeAssistant) -> None:
    """Test we handle powered off during initial configuration."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.epson_test.config_flow.validate_projector",
        side_effect=PoweredOff,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "1.1.1.1"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "powered_off"}


async def test_reconfigure_updates_entry(hass: HomeAssistant) -> None:
    """Test reconfigure flow updates an existing entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Epson Projector",
        data={CONF_CONNECTION_TYPE: HTTP, CONF_HOST: "1.1.1.1", CONF_PORT: "8080"},
        unique_id="12345",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with (
        patch(
            "custom_components.epson_test.config_flow.validate_projector",
            return_value=SimpleNamespace(close=lambda: None),
        ),
        patch(
            "custom_components.epson_test.validate_projector",
            return_value=SimpleNamespace(close=lambda: None),
        ),
        patch("custom_components.epson_test.async_setup_entry", return_value=True),
        patch("custom_components.epson_test.async_unload_entry", return_value=True),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_CONNECTION_TYPE: SERIAL,
                CONF_HOST: "/dev/ttyUSB0",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"
    updated_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert updated_entry is not None
    assert updated_entry.data[CONF_HOST] == "/dev/ttyUSB0"
