# Synthetic Alarm Panel for Home Assistant

A comprehensive Home Assistant integration that provides a synthetic alarm control panel with full UI configuration support. This integration creates a feature-rich alarm panel entity that integrates with your existing Home Assistant scripts and devices.

## Features

- **Multi-Step UI Configuration**: Easy setup through Home Assistant's integration UI
- **Script Integration**: Configure scripts for arm home, disarm home, arm away, and disarm away actions
- **Device Indicators**: Configure LED indicators for armed and alarm states using any switch, light, or binary sensor
- **Full Alarm States**: Supports Off, Home, Away, Arming, and Triggered states
- **HomeKit Compatible**: Works seamlessly with Apple HomeKit integration
- **Dashboard Ready**: Perfect for Home Assistant dashboards with alarm control panel card
- **No External Dependencies**: Pure Home Assistant integration with no hardware requirements
- **HACS Compatible**: Easy installation through HACS

## Installation

### Method 1: HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz) installed
2. Go to HACS → Integrations
3. Click the "⋮" menu → Custom repositories
4. Add this repository URL: `https://github.com/yourusername/ha-synthetic-alarm`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Synthetic Alarm Panel" and install
8. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release or clone this repository
2. Copy the `custom_components/synthetic_alarm` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

The integration uses a 3-step configuration process:

### Step 1: Basic Settings
- **Name**: Display name for your alarm panel
- **Code**: Optional security code (leave empty for no code)
- **Code arm required**: Whether code is needed to arm the system
- **Delay time**: Arming delay in seconds (0-300)
- **Trigger time**: How long alarm sounds when triggered (0-3600)

### Step 2: Script Configuration
Configure scripts to execute when alarm state changes:
- **Arm Home Script**: Script to run when arming in home mode
- **Disarm Home Script**: Script to run when disarming from home mode
- **Arm Away Script**: Script to run when arming in away mode
- **Disarm Away Script**: Script to run when disarming from away mode

### Step 3: Device Indicators
Configure indicator devices (switches, lights, binary sensors):
- **Armed Indicator**: Device to indicate armed status (turns on when armed)
- **Alarm Indicator**: Device to indicate alarm triggered (turns on when alarm is triggered)

All scripts and devices are optional - configure only what you need!

## Usage

Once configured, the integration creates an alarm control panel entity that can be:

### Dashboard Integration
- Add the **Alarm Control Panel** card to your Lovelace dashboard
- Shows current state: Disarmed, Armed Home, Armed Away, Arming, Triggered
- Provides arm/disarm controls with optional code entry
- Works perfectly with Home Assistant's mobile app

### HomeKit Integration
- Automatically compatible with HomeKit integration
- Appears as a security system in Apple Home app
- Supports Siri voice control: "Hey Siri, arm the alarm" / "Hey Siri, disarm the alarm"
- Shows correct status in HomeKit: Off, Home, Away

### Automation Integration
- Use in automations and scripts
- Control via services: `alarm_control_panel.alarm_arm_home`, `alarm_control_panel.alarm_arm_away`, `alarm_control_panel.alarm_disarm`
- React to state changes with automation triggers
- Access configured scripts and indicators through entity attributes

### Real-World Integration
- Connected scripts can control physical devices (lights, sirens, cameras)
- Indicator devices provide visual feedback of alarm status
- Perfect for creating a complete security system with existing HA devices

## Development

This integration serves as a template for building more complex alarm systems. The code is clean and well-documented, making it easy to extend with additional features like:
- Multiple zones/partitions
- Sensor integration
- Custom states
- External API communication

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.