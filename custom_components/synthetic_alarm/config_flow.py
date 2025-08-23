"""Config flow for Synthetic Alarm integration."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


def _get_entity_list(hass: HomeAssistant, domain: str) -> list[str]:
    """Get list of entities for a specific domain."""
    entities = []
    for entity_id in hass.states.async_entity_ids():
        if entity_id.startswith(f"{domain}."):
            entities.append(entity_id)
    return sorted(entities)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Synthetic Alarm."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Store initial data and move to scripts configuration
            self.initial_data = user_input
            return await self.async_step_scripts()

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

    async def async_step_scripts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure scripts for alarm actions."""
        errors = {}

        if user_input is not None:
            # Store script data and move to devices configuration
            self.script_data = user_input
            return await self.async_step_devices()

        # Get available scripts
        script_entities = _get_entity_list(self.hass, "script")
        script_options = [{"value": entity, "label": self.hass.states.get(entity).attributes.get("friendly_name", entity)} for entity in script_entities]

        return self.async_show_form(
            step_id="scripts",
            data_schema=vol.Schema(
                {
                    vol.Optional("script_arm_home"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional("script_disarm_home"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional("script_arm_away"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional("script_disarm_away"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure indicator devices."""
        errors = {}

        if user_input is not None:
            # Create a unique ID for this instance
            await self.async_set_unique_id(f"synthetic_alarm_{self.initial_data['name']}")
            self._abort_if_unique_id_configured()

            # Combine all configuration data
            combined_data = {**self.initial_data, **self.script_data, **user_input}

            # Create the config entry
            return self.async_create_entry(
                title=self.initial_data["name"],
                data=combined_data,
            )

        # Get available switch/light entities for LED indicators
        switch_entities = _get_entity_list(self.hass, "switch")
        light_entities = _get_entity_list(self.hass, "light")
        binary_sensor_entities = _get_entity_list(self.hass, "binary_sensor")
        
        indicator_entities = switch_entities + light_entities + binary_sensor_entities
        indicator_options = [{"value": entity, "label": self.hass.states.get(entity).attributes.get("friendly_name", entity)} for entity in indicator_entities]

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {
                    vol.Optional("armed_indicator"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=indicator_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional("alarm_indicator"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=indicator_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )