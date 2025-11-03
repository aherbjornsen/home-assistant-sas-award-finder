"""SAS Award Finder integration initialization."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_NAME
from .const import DOMAIN
from .sensor import SASAwardFinderCoordinator

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration via configuration.yaml (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SAS Award Finder from a config entry."""
    config = entry.data
    name = config.get(CONF_NAME)
    origin = config.get("origin")
    destinations = config.get("destinations")
    month = config.get("month")
    direct = config.get("direct", False)
    market = config.get("market", "no-no")

    # Create coordinator
    coordinator = SASAwardFinderCoordinator(hass, origin, destinations, month, direct, market)
    await coordinator.async_refresh()

    # Store coordinator for unloading later
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward setup to sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove coordinator
    coordinator = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    # Unload all platforms (sensor)
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, ["sensor"])

    return unload_ok
