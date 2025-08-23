"""Config flow for Synthetic Alarm integration."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Synthetic Alarm."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Create a unique ID for this instance
            await self.async_set_unique_id(f"synthetic_alarm_{user_input['name']}")
            self._abort_if_unique_id_configured()

            # Create the config entry
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default="Synthetic Alarm"): cv.string,
                    vol.Optional("code", default=""): cv.string,
                    vol.Optional("code_arm_required", default=False): cv.boolean,
                    vol.Optional("delay_time", default=30): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=300)
                    ),
                    vol.Optional("trigger_time", default=600): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=3600)
                    ),
                }
            ),
            errors=errors,
        )