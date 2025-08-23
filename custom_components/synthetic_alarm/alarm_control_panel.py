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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER

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

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if self._code and code != self._code:
            _LOGGER.warning("Invalid code provided for disarming")
            return
        
        self._state = AlarmControlPanelState.DISARMED
        self.async_write_ha_state()

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