"""The epson integration."""

import logging
from typing import TYPE_CHECKING

import aiohttp
from epson_projector import Projector  # type: ignore[import]
from epson_projector.const import (  # type: ignore[import]
    PWR_OFF_STATE,
    STATE_UNAVAILABLE as EPSON_STATE_UNAVAILABLE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import (
    async_create_clientsession,
)

from .const import CONF_CONNECTION_TYPE, DOMAIN, ESCVPNET, HTTP
from .exceptions import CannotConnect, PoweredOff
from .services import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.MEDIA_PLAYER, Platform.SENSOR, Platform.REMOTE]

_LOGGER = logging.getLogger(__name__)

type EpsonConfigEntry = ConfigEntry[Projector]


async def validate_projector(
    hass: HomeAssistant,
    host: str,
    conn_type: str,
    check_power: bool = True,
    check_powered_on: bool = False,
    port: str | None = None,
    password: str | None = None,
) -> Projector:
    """Validate the given projector host allows us to connect."""
    middlewares = []
    if password:
        _LOGGER.info("Using password for authentication")
        digest_auth = aiohttp.DigestAuthMiddleware(
            login="EPSONWEB", password=password
        )
        middlewares.append(digest_auth)

    session = async_create_clientsession(hass, verify_ssl=False, middlewares=middlewares)

    epson_proj = Projector(
        host=host,
        websession=session,
        type=conn_type,
        tcp_password=password,
    )

    if port:
        if conn_type == HTTP:
            epson_proj._projector._http_url = epson_proj._projector._http_url.replace(  # noqa: SLF001 # pyright: ignore[reportAttributeAccessIssue]
                ":80/", f":{port}/"
            )
        elif conn_type == ESCVPNET:
            epson_proj._projector._port = int(port) # pyright: ignore[reportAttributeAccessIssue]  # noqa: SLF001

    if check_power:
        _power = await epson_proj.get_power()
        if not _power or _power == EPSON_STATE_UNAVAILABLE:
            _LOGGER.debug("Cannot connect to projector")
            raise CannotConnect
        if _power == PWR_OFF_STATE and check_powered_on:
            _LOGGER.debug("Projector is off")
            raise PoweredOff
    return epson_proj


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: EpsonConfigEntry) -> bool:
    """Set up epson from a config entry."""
    projector = await validate_projector(
        hass=hass,
        host=entry.data[CONF_HOST],
        conn_type=entry.data[CONF_CONNECTION_TYPE],
        check_power=False,
        check_powered_on=False,
        port=entry.data.get(CONF_PORT),
        password=entry.data.get(CONF_PASSWORD),
    )
    entry.runtime_data = projector
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(projector.close)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EpsonConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: EpsonConfigEntry
) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version == 1 and config_entry.minor_version == 1:
        new_data = {**config_entry.data}
        new_data[CONF_CONNECTION_TYPE] = HTTP

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, version=1, minor_version=2
        )

    _LOGGER.debug(
        "Migration to configuration version %s successful", config_entry.version
    )

    return True
