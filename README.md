# Synthetic Alarm Panel for Home Assistant

A simplified Home Assistant integration that provides a synthetic alarm control panel with UI configuration support. This integration creates a basic alarm panel entity that can be used for testing, development, or as a template for building more complex alarm systems.

## Features

- **UI Configuration**: Easy setup through Home Assistant's integration UI
- **Configurable Settings**: Customizable name, security code, timing settings
- **Basic Alarm Functions**: Arm Home, Arm Away, Disarm
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

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Synthetic Alarm Panel"
4. Configure the following options:
   - **Name**: Display name for your alarm panel
   - **Code**: Optional security code (leave empty for no code)
   - **Code arm required**: Whether code is needed to arm the system
   - **Delay time**: Arming delay in seconds (0-300)
   - **Trigger time**: How long alarm sounds when triggered (0-3600)

## Usage

Once configured, the integration creates an alarm control panel entity that can be:
- Added to your Lovelace dashboard
- Used in automations
- Controlled via services and scripts
- Integrated with other Home Assistant components

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