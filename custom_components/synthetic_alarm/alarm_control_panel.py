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
from homeassistant.helpers.event import async_track_state_change_event
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
    _attr_code_format = None
    _attr_code_arm_required = False

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
        
        # Log configuration for debugging
        _LOGGER.info("Synthetic Alarm Panel '%s' added to HA", self._attr_name)
        _LOGGER.info("Configured scripts:")
        _LOGGER.info("  - Arm Home: %s", self._script_arm_home)
        _LOGGER.info("  - Disarm Home: %s", self._script_disarm_home)
        _LOGGER.info("  - Arm Away: %s", self._script_arm_away)
        _LOGGER.info("  - Disarm Away: %s", self._script_disarm_away)
        _LOGGER.info("Configured input sensors (feedback from external system):")
        _LOGGER.info("  - Armed Sensor: %s", self._armed_indicator)
        _LOGGER.info("  - Alarm Sensor: %s", self._alarm_indicator)
        _LOGGER.info("Timing settings:")
        _LOGGER.info("  - Delay Time: %s seconds", self._delay_time)
        _LOGGER.info("  - Trigger Time: %s seconds", self._trigger_time)
        _LOGGER.info("Code requirement: DISABLED (no code needed)")
        
        # Verify script entities exist
        if self._script_arm_home and not self.hass.states.get(self._script_arm_home):
            _LOGGER.warning("Arm Home script entity %s does not exist!", self._script_arm_home)
        if self._script_disarm_home and not self.hass.states.get(self._script_disarm_home):
            _LOGGER.warning("Disarm Home script entity %s does not exist!", self._script_disarm_home)
        if self._script_arm_away and not self.hass.states.get(self._script_arm_away):
            _LOGGER.warning("Arm Away script entity %s does not exist!", self._script_arm_away)
        if self._script_disarm_away and not self.hass.states.get(self._script_disarm_away):
            _LOGGER.warning("Disarm Away script entity %s does not exist!", self._script_disarm_away)
        
        # Set up state change listeners for binary sensors
        if self._armed_indicator:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, [self._armed_indicator], self._sensor_state_changed
                )
            )
        if self._alarm_indicator:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, [self._alarm_indicator], self._sensor_state_changed
                )
            )
        
        # Initial sensor state check
        await self._monitor_sensors()

    async def _sensor_state_changed(self, event) -> None:
        """Handle sensor state changes."""
        _LOGGER.info("Sensor state changed: %s", event.data)
        await self._monitor_sensors()

    @property
    def state(self) -> AlarmControlPanelState:
        """Return the state of the alarm control panel."""
        return self._state

    @property
    def code_format(self) -> str | None:
        """Return the code format if a code is required."""
        return None  # No code required
    
    @property
    def code_arm_required(self) -> bool:
        """Return if the code is required for arming."""
        return False
    
    @property 
    def code_disarm_required(self) -> bool:
        """Return if the code is required for disarming."""
        return False

    async def _call_script(self, script_entity_id: str | None) -> None:
        """Call a script if configured."""
        _LOGGER.info("_call_script called with entity_id: %s", script_entity_id)
        
        if not script_entity_id:
            _LOGGER.info("No script configured, skipping script execution")
            return
            
        if not self._hass:
            _LOGGER.error("HomeAssistant instance not available for script execution")
            return
            
        try:
            _LOGGER.info("About to call script: %s", script_entity_id)
            script_name = script_entity_id.split(".", 1)[1]
            _LOGGER.info("Extracted script name: %s", script_name)
            
            # Check if script exists
            if not self._hass.states.get(script_entity_id):
                _LOGGER.error("Script entity %s does not exist!", script_entity_id)
                return
            
            _LOGGER.info("Script entity exists, calling service immediately...")
            # Use blocking=False for immediate execution
            await self._hass.services.async_call(
                "script",
                script_name,
                blocking=False
            )
            _LOGGER.info("Successfully called script (non-blocking): %s", script_entity_id)
        except Exception as err:
            _LOGGER.error("Failed to call script %s: %s", script_entity_id, err)
            _LOGGER.exception("Full exception details:")

    async def _monitor_sensors(self) -> None:
        """Monitor binary sensors and update alarm state accordingly."""
        if not self._hass:
            return
            
        # Check armed sensor
        if self._armed_indicator:
            armed_state = self._hass.states.get(self._armed_indicator)
            if armed_state:
                is_armed = armed_state.state == "on"
                _LOGGER.info("Armed sensor %s state: %s (armed: %s)", self._armed_indicator, armed_state.state, is_armed)
                
                # Update alarm state based on sensor
                if is_armed and self._state == AlarmControlPanelState.ARMING:
                    # Transition from arming to armed (determine home vs away based on last command)
                    if hasattr(self, '_pending_arm_mode'):
                        self._state = self._pending_arm_mode
                        delattr(self, '_pending_arm_mode')
                    else:
                        self._state = AlarmControlPanelState.ARMED_AWAY  # Default
                    self.async_write_ha_state()
                    _LOGGER.info("Transitioned to %s based on armed sensor", self._state)
                elif not is_armed and self._state in [AlarmControlPanelState.ARMED_HOME, AlarmControlPanelState.ARMED_AWAY]:
                    # Armed sensor went off, system is disarmed
                    self._state = AlarmControlPanelState.DISARMED
                    self.async_write_ha_state()
                    _LOGGER.info("Transitioned to DISARMED based on armed sensor")
        
        # Check alarm sensor
        if self._alarm_indicator:
            alarm_state = self._hass.states.get(self._alarm_indicator)
            if alarm_state:
                is_triggered = alarm_state.state == "on"
                _LOGGER.info("Alarm sensor %s state: %s (triggered: %s)", self._alarm_indicator, alarm_state.state, is_triggered)
                
                if is_triggered and self._state != AlarmControlPanelState.TRIGGERED:
                    # Alarm was triggered by external system
                    self._state = AlarmControlPanelState.TRIGGERED
                    self.async_write_ha_state()
                    _LOGGER.info("Alarm TRIGGERED based on alarm sensor")
                elif not is_triggered and self._state == AlarmControlPanelState.TRIGGERED:
                    # Alarm sensor cleared, back to disarmed
                    self._state = AlarmControlPanelState.DISARMED
                    self.async_write_ha_state()
                    _LOGGER.info("Alarm cleared, back to DISARMED based on alarm sensor")

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        _LOGGER.info("async_alarm_disarm called")
        
        current_state = self._state
        _LOGGER.info("Disarming from state: %s", current_state)
        
        # Call appropriate disarm script IMMEDIATELY based on current state
        if current_state == AlarmControlPanelState.ARMED_HOME:
            _LOGGER.info("Calling disarm home script immediately: %s", self._script_disarm_home)
            await self._call_script(self._script_disarm_home)
        elif current_state == AlarmControlPanelState.ARMED_AWAY:
            _LOGGER.info("Calling disarm away script immediately: %s", self._script_disarm_away)
            await self._call_script(self._script_disarm_away)
        else:
            _LOGGER.info("No disarm script to call for previous state: %s", current_state)
        
        # Script will control external system, sensors will update our state
        _LOGGER.info("Disarm script executed, waiting for sensor feedback to update state")
        _LOGGER.info("Disarm sequence complete")

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        _LOGGER.info("async_alarm_arm_home called")
        
        _LOGGER.info("Starting arm home sequence, delay_time: %s", self._delay_time)
        
        # Set pending mode for sensor feedback
        self._pending_arm_mode = AlarmControlPanelState.ARMED_HOME
        
        # Call arm home script IMMEDIATELY before any delays
        _LOGGER.info("Calling arm home script immediately: %s", self._script_arm_home)
        await self._call_script(self._script_arm_home)
        
        if self._delay_time > 0:
            _LOGGER.info("Entering ARMING state for %s seconds", self._delay_time)
            self._state = AlarmControlPanelState.ARMING
            self.async_write_ha_state()
            
            # Wait for delay or sensor feedback
            await asyncio.sleep(self._delay_time)
            
            # If still arming after delay, check sensors or default to armed
            if self._state == AlarmControlPanelState.ARMING:
                await self._monitor_sensors()
                # If still arming and no sensor feedback, assume success
                if self._state == AlarmControlPanelState.ARMING:
                    _LOGGER.info("No sensor feedback, defaulting to ARMED_HOME")
                    self._state = AlarmControlPanelState.ARMED_HOME
                    self.async_write_ha_state()
        else:
            # No delay, monitor sensors immediately
            await self._monitor_sensors()
        
        _LOGGER.info("Arm home sequence complete")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        _LOGGER.info("async_alarm_arm_away called")
        
        _LOGGER.info("Starting arm away sequence, delay_time: %s", self._delay_time)
        
        # Set pending mode for sensor feedback
        self._pending_arm_mode = AlarmControlPanelState.ARMED_AWAY
        
        # Call arm away script IMMEDIATELY before any delays
        _LOGGER.info("Calling arm away script immediately: %s", self._script_arm_away)
        await self._call_script(self._script_arm_away)
        
        if self._delay_time > 0:
            _LOGGER.info("Entering ARMING state for %s seconds", self._delay_time)
            self._state = AlarmControlPanelState.ARMING
            self.async_write_ha_state()
            
            # Wait for delay or sensor feedback
            await asyncio.sleep(self._delay_time)
            
            # If still arming after delay, check sensors or default to armed
            if self._state == AlarmControlPanelState.ARMING:
                await self._monitor_sensors()
                # If still arming and no sensor feedback, assume success
                if self._state == AlarmControlPanelState.ARMING:
                    _LOGGER.info("No sensor feedback, defaulting to ARMED_AWAY")
                    self._state = AlarmControlPanelState.ARMED_AWAY
                    self.async_write_ha_state()
        else:
            # No delay, monitor sensors immediately
            await self._monitor_sensors()
        
        _LOGGER.info("Arm away sequence complete")

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