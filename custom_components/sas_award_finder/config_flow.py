from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from .const import DOMAIN, DEFAULT_MARKET


class SASAwardFinderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for SAS Award Finder."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="SAS Award Finder"): str,
            vol.Required("origin"): str,
            vol.Required("destinations"): str,
            vol.Required("month"): str,
            vol.Optional("direct", default=False): bool,
            vol.Optional("market", default=DEFAULT_MARKET): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
