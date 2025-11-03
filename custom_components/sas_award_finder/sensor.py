from __future__ import annotations
import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, BASE_URL, DEFAULT_MARKET

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=1)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up SAS Award Finder sensor from config entry."""
    config = entry.data
    name = config.get(CONF_NAME)
    origin = config.get("origin")
    destinations = config.get("destinations")
    month = config.get("month")
    direct = config.get("direct", False)
    market = config.get("market", DEFAULT_MARKET)

    coordinator = SASAwardFinderCoordinator(hass, origin, destinations, month, direct, market)

    # Immediately fetch the first update
    await coordinator.async_refresh()

    async_add_entities([SASAwardFinderSensor(coordinator, name)])


class SASAwardFinderCoordinator(DataUpdateCoordinator):
    """Handle fetching data from SAS API."""

    def __init__(self, hass: HomeAssistant, origin, destinations, month, direct, market):
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

        _LOGGER.debug("Fetching SAS Award data from URL: %s", url)

        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(15):
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"Error {resp.status} fetching {url}")
                        data = await resp.json()

                        # Normalize to always return a list
                        if isinstance(data, dict):
                            data = [data]
                        elif not isinstance(data, list):
                            data = []

                        return data
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class SASAwardFinderSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for SAS Award Finder."""

    def __init__(self, coordinator: SASAwardFinderCoordinator, name: str):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"sas_award_{name.lower().replace(' ', '_')}"

    @property
    def native_value(self):
        """Return 'True' if any availability found, otherwise 'False'."""
        data = self.coordinator.data
        if not data:
            return "False"

        try:
            all_outbound = []
            all_inbound = []

            for dest_info in data:
                avail = dest_info.get("availability", {})
                all_outbound.extend(avail.get("outbound", []))
                all_inbound.extend(avail.get("inbound", []))

            has_data = len(all_outbound) > 0 or len(all_inbound) > 0
            return str(has_data)
        except Exception as e:
            _LOGGER.error("Error computing sensor state: %s", e)
            return "False"

    @property
    def extra_state_attributes(self):
        """Return only flattened outbound/inbound arrays suitable for Flex Table Card."""
        data = self.coordinator.data
        if not data:
            return {}
    
        try:
            all_outbound = []
            all_inbound = []
    
            # Merge outbound/inbound flights from multiple destinations
            for dest_info in data:
                avail = dest_info.get("availability", {})
    
                # Flatten outbound
                for f in avail.get("outbound", []):
                    all_outbound.append({
                        "date": f.get("date"),
                        "AG": f.get("AG"),
                        "AP": f.get("AP"),
                        "availableSeatsTotal": f.get("availableSeatsTotal")
                    })
    
                # Flatten inbound
                for f in avail.get("inbound", []):
                    all_inbound.append({
                        "date": f.get("date"),
                        "AG": f.get("AG"),
                        "AP": f.get("AP"),
                        "availableSeatsTotal": f.get("availableSeatsTotal")
                    })
    
            return {
                "outbound_table": all_outbound,
                "inbound_table": all_inbound,
                "total_outbound": len(all_outbound),
                "total_inbound": len(all_inbound),
            }
    
        except Exception as e:
            _LOGGER.error("Error parsing attributes: %s", e)
            return {}
