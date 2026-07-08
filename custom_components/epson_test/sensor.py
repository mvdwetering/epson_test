from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    import epson_projector  # type: ignore[import]
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

from epson_projector import ProjectorUnavailableError  # type: ignore[import]

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class EpsonSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[epson_projector.Projector], Coroutine[None, None, StateType]]


ENTITY_DESCRIPTIONS = [
    EpsonSensorEntityDescription(
        key="lamp_hours",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="h",
        value_fn=lambda projector: projector.get("LAMP")   # projector.get_lamp_hours(),
    )
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    entities: list[SensorEntity] = [
        EpsonSensor(
            projector=config_entry.runtime_data,
            unique_id=config_entry.unique_id or config_entry.entry_id,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    ]

    async_add_entities(entities, update_before_add=True)


class EpsonSensor(SensorEntity):
    """Representation of a Epson sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        projector: epson_projector.Projector,
        unique_id: str,
        entity_description: EpsonSensorEntityDescription,
    ) -> None:
        self.projector = projector
        self.entity_description: EpsonSensorEntityDescription = entity_description
        self._attr_translation_key = self.entity_description.key

        self._attr_unique_id = f"{self.entity_description.key}_{unique_id}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, unique_id)})

    async def async_update(self) -> None:
        self._attr_native_value = await self.entity_description.value_fn(self.projector)
