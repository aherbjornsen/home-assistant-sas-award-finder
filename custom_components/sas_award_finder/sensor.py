from __future__ import annotations
import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, BASE_URL, DEFAULT_MARKET

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=1)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor from config entry."""
    config = entry.data
    name = config.get(CONF_NAME)
    origin = config.get("origin")
    destinations = config.get("destinations")
    month = config.get("month")
    direct = config.get("direct", False)
    market = config.get("market", DEFAULT_MARKET)

    coordinator = SASAwardFinderCoordinator(hass, origin, destinations, month, direct, market)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([SASAwardFinderSensor(coordinator, name)], update_before_add=True)


class SASAwardFinderCoordinator(DataUpdateCoordinator):
    """Handle fetching data from SAS API."""

    def __init__(self, hass, origin, destinations, month, direct, market):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.origin = origin
        self.destinations = destinations
        self.month = month.replace("-", "")
        self.direct = str(direct).lower()
        self.market = market

    async def _async_update_data(self):
        """Fetch data from SAS Award Finder API."""
        url = (
            f"{BASE_URL}?market={self.market}"
            f"&origin={self.origin}"
            f"&destinations={self.destinations}"
            f"&selectedMonth={self.month}"
            f"&passengers=2&direct={self.direct}&availability=true"
        )

        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(15):
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"Error {resp.status} fetching {url}")
                        return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class SASAwardFinderSensor(SensorEntity):
    """Sensor entity for SAS Award Finder."""

    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._attr_name = name
        self._attr_unique_id = f"sas_award_{name.lower().replace(' ', '_')}"

    @property
    def native_value(self):
        """Short summary shown in HA."""
        data = self.coordinator.data
        if not data:
            return "No data"
        try:
            dest = data[0].get("cityName", "")
            available_days = len(data[0]["availability"].get("outbound", []))
            return f"{dest}: {available_days} days"
        except Exception:
            return "Error"

    @property
    def extra_state_attributes(self):
        """Detailed JSON attributes for dashboards."""
        if not self.coordinator.data:
            return {}
        try:
            dest_info = self.coordinator.data[0]
            return {
                "airport": dest_info.get("airportName"),
                "city": dest_info.get("cityName"),
                "outbound": dest_info["availability"].get("outbound", []),
                "inbound": dest_info["availability"].get("inbound", []),
                "url": f"https://www.sas.no/award-finder?origin={self.coordinator.origin}&destination={self.coordinator.destinations}"
            }
        except Exception as e:
            _LOGGER.error("Error parsing attributes: %s", e)
            return {}
