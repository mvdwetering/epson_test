from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from epson_projector import (  # type: ignore[import]
    KeyCodes,
    Projector,
    ProjectorUnavailableError,
)
from epson_projector.const import (  # type: ignore[import]
    EPSON_CODES,
    POWER,
)
from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

KEYCODE_MAP = {
    "power_on": KeyCodes.POWER_ON,
    "power_off": KeyCodes.POWER_OFF,
    "menu": KeyCodes.MENU,
    "up": KeyCodes.POINTER_UP,
    "down": KeyCodes.POINTER_DOWN,
    "left": KeyCodes.POINTER_LEFT,
    "right": KeyCodes.POINTER_RIGHT,
    "enter": KeyCodes.ENTER,
    "esc": KeyCodes.ESC,
}

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            EpsonRemote(
                projector=config_entry.runtime_data,
                unique_id=config_entry.unique_id or config_entry.entry_id,
            )
        ]
    )


class EpsonRemote(RemoteEntity):
    """Representation of a remote of an Epson projector."""

    _attr_has_entity_name = True

    def __init__(
        self,
        projector: Projector,
        unique_id: str,
    ) -> None:
        self._projector = projector
        self._attr_unique_id = f"remote_{unique_id}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, unique_id)})

        self._power_state: bool = False

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self._power_state

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Send the power on command."""
        await self.async_send_command(["power_on"])

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Send the power off command."""
        await self.async_send_command(["power_off"])

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send commands to a device."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, DEFAULT_NUM_REPEATS)
        delay_secs = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)

        first = True
        for _ in range(num_repeats):
            for cmd in command:
                if not first:
                    await asyncio.sleep(delay_secs)
                first = False

                await self._projector.send_key(KEYCODE_MAP[cmd])

    async def async_update(self) -> None:
        """Update state of device."""
        try:
            epson_power = await self._projector.get_power()
            self._power_state = epson_power == EPSON_CODES[POWER]
        except ProjectorUnavailableError as ex:
            _LOGGER.debug("Projector is unavailable: %s", ex)
            self._attr_available = False
            return
