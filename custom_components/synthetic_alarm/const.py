"""Constants for the Synthetic Alarm integration."""

from homeassistant.const import Platform

DOMAIN = "synthetic_alarm"

DEFAULT_NAME = "Synthetic Alarm"
MANUFACTURER = "Synthetic"

PLATFORMS = [Platform.ALARM_CONTROL_PANEL]

# Configuration keys for scripts
CONF_SCRIPT_ARM_HOME = "script_arm_home"
CONF_SCRIPT_DISARM_HOME = "script_disarm_home"
CONF_SCRIPT_ARM_AWAY = "script_arm_away"
CONF_SCRIPT_DISARM_AWAY = "script_disarm_away"

# Configuration keys for indicator devices
CONF_ARMED_INDICATOR = "armed_indicator"
CONF_ALARM_INDICATOR = "alarm_indicator"

# Default values
DEFAULT_DELAY_TIME = 30
DEFAULT_TRIGGER_TIME = 600