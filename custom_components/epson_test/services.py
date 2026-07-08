"""Support for Epson projector."""

from epson_projector.const import CMODE_LIST_SET  # type: ignore[import]
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, service
import voluptuous as vol

from .const import ATTR_CMODE, DOMAIN

SERVICE_SELECT_CMODE = "select_cmode"
SERVICE_SEND_RAW_COMMAND = "send_raw_command"

ATTR_RAW_COMMAND = "raw_command"
ATTR_RESPONSE = "response"


async def async_handle_send_raw_command(
    hass: HomeAssistant, call: ServiceCall
) -> ServiceResponse:
    """Send a raw command to the configured projector and return its response."""
    config_entry_id = call.data[ATTR_CONFIG_ENTRY_ID]
    config_entry = hass.config_entries.async_get_entry(config_entry_id)

    if config_entry is None or config_entry.state is not ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="config_entry_not_found",
            translation_placeholders={"config_entry_id": config_entry_id},
        )

    response = await config_entry.runtime_data.send_raw(call.data[ATTR_RAW_COMMAND])
    return {ATTR_RESPONSE: response}


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""
    async def async_handle_send_raw_command_local(call: ServiceCall) -> ServiceResponse:
        return await async_handle_send_raw_command(hass, call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_RAW_COMMAND,
        async_handle_send_raw_command_local,
        schema=vol.Schema(
            {
                vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
                vol.Required(ATTR_RAW_COMMAND): cv.string,
            }
        ),
        supports_response=SupportsResponse.ONLY,
    )

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_SELECT_CMODE,
        entity_domain=MEDIA_PLAYER_DOMAIN,
        schema={vol.Required(ATTR_CMODE): vol.All(cv.string, vol.Any(*CMODE_LIST_SET))},
        func=SERVICE_SELECT_CMODE,
    )
