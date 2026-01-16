# Exergy - Bitaxe Integration for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/exergyheat/ha-integration-bitaxe.svg)](https://github.com/exergyheat/ha-integration-bitaxe/releases)
[![License](https://img.shields.io/github/license/exergyheat/ha-integration-bitaxe.svg)](LICENSE)

Monitor and control your [Bitaxe](https://github.com/bitaxeorg/ESP-Miner) Bitcoin mining devices directly from Home Assistant.

## Features

- **Real-time Mining Metrics**: Monitor hashrate, shares, difficulty, and error rates
- **Hardware Monitoring**: Track temperature, voltage, power consumption, and fan speed
- **Full Device Control**: Adjust frequency, voltage, fan speed, and temperature targets
- **Device Management**: Restart devices, trigger identification LED, and configure display settings
- **Local Communication**: All data stays on your network - no cloud required

## Supported Entities

### Sensors (15 entities)
| Entity | Description | Unit |
|--------|-------------|------|
| Hashrate | Current hashrate | GH/s |
| Hashrate (1m/10m/1h avg) | Rolling averages | GH/s |
| Shares Accepted | Total accepted shares | - |
| Shares Rejected | Total rejected shares | - |
| Error Rate | Rejection percentage | % |
| Pool Difficulty | Current pool difficulty | - |
| Best Difficulty | Best all-time difficulty | - |
| Best Session Difficulty | Best difficulty this session | - |
| Chip Temperature | ASIC chip temperature | °C |
| VR Temperature | Voltage regulator temperature | °C |
| Input Voltage | Input voltage | mV |
| Core Voltage | ASIC core voltage | mV |
| Power | Power consumption | W |
| Fan Speed | Fan speed percentage | % |
| Uptime | Device uptime | seconds |

### Switches (3 entities)
| Entity | Description |
|--------|-------------|
| Auto Fan Speed | Enable/disable automatic fan control |
| Overclock Enabled | Enable/disable overclocking |
| Invert Screen | Invert the device display |

### Numbers (6 entities)
| Entity | Description | Range |
|--------|-------------|-------|
| Core Voltage | ASIC core voltage | 1000-1400 mV |
| Frequency | Mining frequency | 100-1000 MHz |
| Fan Speed (Manual) | Manual fan speed | 0-100% |
| Temperature Target | Target temperature | 30-100°C |
| Display Timeout | Screen timeout | -1 to 240 min |
| Statistics Frequency | Stats update interval | 0-600 sec |

### Selects (1 entity)
| Entity | Description | Options |
|--------|-------------|---------|
| Screen Rotation | Display orientation | 0°, 90°, 180°, 270° |

### Buttons (3 entities)
| Entity | Description |
|--------|-------------|
| Update | Manually refresh device data |
| Restart | Restart the Bitaxe device |
| Identify | Flash the identification LED |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/exergyheat/ha-integration-bitaxe` as an Integration
5. Click "Add"
6. Search for "Exergy - Bitaxe" and install it
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/exergyheat/ha-integration-bitaxe/releases)
2. Extract and copy the `custom_components/bitaxe` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Exergy - Bitaxe"
4. Enter your Bitaxe device's IP address
5. Configure the device name, port (default: 80), and scan interval (default: 15 seconds)

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| Host | Required | IP address of your Bitaxe device |
| Port | 80 | HTTP port (usually 80) |
| Scan Interval | 15 | How often to poll the device (5-300 seconds) |

## Requirements

- Home Assistant 2024.1.0 or newer
- Bitaxe device running ESP-Miner firmware
- Network connectivity to your Bitaxe device

## Troubleshooting

### Device not connecting
- Verify the IP address is correct
- Ensure your Bitaxe is powered on and connected to your network
- Check that Home Assistant can reach the device (ping test)
- Confirm the Bitaxe web interface is accessible at `http://<ip-address>`

### Entities showing unavailable
- The integration marks the device unavailable after 3 consecutive failed polls
- Check network connectivity
- Verify the device hasn't crashed or rebooted

### Incorrect readings
- Some sensors are disabled by default (WiFi signal, heap memory)
- Enable them in the entity settings if needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Bitaxe](https://github.com/bitaxeorg) - The open-source Bitcoin ASIC miner project
- [ESP-Miner](https://github.com/bitaxeorg/ESP-Miner) - The firmware powering Bitaxe devices
