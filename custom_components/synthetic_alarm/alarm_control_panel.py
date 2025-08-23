"""Support for Synthetic Alarm control panel."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import SERVICE_TURN_ON, SERVICE_TURN_OFF

from .const import (
    DOMAIN, 
    MANUFACTURER,
    CONF_SCRIPT_ARM_HOME,
    CONF_SCRIPT_DISARM_HOME,
    CONF_SCRIPT_ARM_AWAY,
    CONF_SCRIPT_DISARM_AWAY,
    CONF_ARMED_INDICATOR,
    CONF_ALARM_INDICATOR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the alarm control panel platform."""
    config = hass.data[DOMAIN][entry.entry_id]
    
    alarm = SyntheticAlarmControlPanel(entry.entry_id, config)
    async_add_entities([alarm])


class SyntheticAlarmControlPanel(AlarmControlPanelEntity):
    """Representation of a Synthetic Alarm control panel."""

    _attr_should_poll = False
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(self, entry_id: str, config: dict[str, Any]) -> None:
        """Initialize the alarm control panel."""
        self._entry_id = entry_id
        self._config = config
        self._hass = None  # Will be set in async_added_to_hass
        self._attr_name = config.get("name", "Synthetic Alarm")
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": self._attr_name,
            "manufacturer": MANUFACTURER,
            "model": "Synthetic Alarm Panel",
        }
        
        self._state = AlarmControlPanelState.DISARMED
        self._code = config.get("code", "")
        self._code_arm_required = config.get("code_arm_required", False)
        self._delay_time = config.get("delay_time", 30)
        self._trigger_time = config.get("trigger_time", 600)
        
        # Script entity IDs
        self._script_arm_home = config.get(CONF_SCRIPT_ARM_HOME)
        self._script_disarm_home = config.get(CONF_SCRIPT_DISARM_HOME)
        self._script_arm_away = config.get(CONF_SCRIPT_ARM_AWAY)
        self._script_disarm_away = config.get(CONF_SCRIPT_DISARM_AWAY)
        
        # Indicator device entity IDs
        self._armed_indicator = config.get(CONF_ARMED_INDICATOR)
        self._alarm_indicator = config.get(CONF_ALARM_INDICATOR)

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self._hass = self.hass

    @property
    def state(self) -> AlarmControlPanelState:
        """Return the state of the alarm control panel."""
        return self._state

    @property
    def code_format(self) -> str | None:
        """Return the code format if a code is required."""
        if self._code:
            return "number"
        return None

    async def _call_script(self, script_entity_id: str | None) -> None:
        """Call a script if configured."""
        if script_entity_id and self._hass:
            try:
                await self._hass.services.async_call(
                    "script",
                    script_entity_id.split(".", 1)[1],
                    blocking=True
                )
                _LOGGER.debug("Called script: %s", script_entity_id)
            except Exception as err:
                _LOGGER.error("Failed to call script %s: %s", script_entity_id, err)

    async def _update_indicator(self, entity_id: str | None, turn_on: bool) -> None:
        """Update an indicator device."""
        if entity_id and self._hass:
            try:
                domain = entity_id.split(".", 1)[0]
                service = SERVICE_TURN_ON if turn_on else SERVICE_TURN_OFF
                await self._hass.services.async_call(
                    domain,
                    service,
                    {"entity_id": entity_id},
                    blocking=False
                )
                _LOGGER.debug("Updated indicator %s: %s", entity_id, "ON" if turn_on else "OFF")
            except Exception as err:
                _LOGGER.error("Failed to update indicator %s: %s", entity_id, err)

    async def _update_indicators(self) -> None:
        """Update all indicator devices based on current state."""
        is_armed = self._state in [
            AlarmControlPanelState.ARMED_HOME,
            AlarmControlPanelState.ARMED_AWAY,
        ]
        is_triggered = self._state == AlarmControlPanelState.TRIGGERED
        
        await self._update_indicator(self._armed_indicator, is_armed)
        await self._update_indicator(self._alarm_indicator, is_triggered)

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if self._code and code != self._code:
            _LOGGER.warning("Invalid code provided for disarming")
            return
        
        current_state = self._state
        self._state = AlarmControlPanelState.DISARMED
        self.async_write_ha_state()
        
        # Call appropriate disarm script based on previous state
        if current_state == AlarmControlPanelState.ARMED_HOME:
            await self._call_script(self._script_disarm_home)
        elif current_state == AlarmControlPanelState.ARMED_AWAY:
            await self._call_script(self._script_disarm_away)
        
        # Update indicators
        await self._update_indicators()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        if self._code_arm_required and self._code and code != self._code:
            _LOGGER.warning("Invalid code provided for arming home")
            return
        
        if self._delay_time > 0:
            self._state = AlarmControlPanelState.ARMING
            self.async_write_ha_state()
            await asyncio.sleep(self._delay_time)
        
        self._state = AlarmControlPanelState.ARMED_HOME
        self.async_write_ha_state()
        
        # Call arm home script
        await self._call_script(self._script_arm_home)
        
        # Update indicators
        await self._update_indicators()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        if self._code_arm_required and self._code and code != self._code:
            _LOGGER.warning("Invalid code provided for arming away")
            return
        
        if self._delay_time > 0:
            self._state = AlarmControlPanelState.ARMING
            self.async_write_ha_state()
            await asyncio.sleep(self._delay_time)
        
        self._state = AlarmControlPanelState.ARMED_AWAY
        self.async_write_ha_state()
        
        # Call arm away script
        await self._call_script(self._script_arm_away)
        
        # Update indicators
        await self._update_indicators()

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Trigger the alarm."""
        self._state = AlarmControlPanelState.TRIGGERED
        self.async_write_ha_state()
        
        # Update indicators
        await self._update_indicators()
        
        # Auto-reset after trigger time
        if self._trigger_time > 0:
            await asyncio.sleep(self._trigger_time)
            self._state = AlarmControlPanelState.DISARMED
            self.async_write_ha_state()
            await self._update_indicators()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {
            "configured_scripts": {
                "arm_home": self._script_arm_home,
                "disarm_home": self._script_disarm_home,
                "arm_away": self._script_arm_away,
                "disarm_away": self._script_disarm_away,
            },
            "configured_indicators": {
                "armed": self._armed_indicator,
                "alarm": self._alarm_indicator,
            },
        }
        return attrs