"""Sensor platform for Bitaxe integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfInformation,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, GIGA_HASH_PER_SECOND
from .coordinator import BitaxeDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bitaxe sensors from a config entry."""
    coordinator: BitaxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        # Mining metrics
        BitaxeHashrateSensor(coordinator, "hashRate", "Hashrate"),
        BitaxeHashrateSensor(coordinator, "hashRate_1m", "Hashrate (1m avg)"),
        BitaxeHashrateSensor(coordinator, "hashRate_10m", "Hashrate (10m avg)"),
        BitaxeHashrateSensor(coordinator, "hashRate_1h", "Hashrate (1h avg)"),
        BitaxeSharesSensor(coordinator, "sharesAccepted", "Shares Accepted"),
        BitaxeSharesSensor(coordinator, "sharesRejected", "Shares Rejected"),
        BitaxePercentageSensor(coordinator, "errorPercentage", "Error Rate"),
        BitaxeDifficultySensor(coordinator, "poolDifficulty", "Pool Difficulty"),
        BitaxeDifficultySensor(coordinator, "bestDiff", "Best Difficulty"),
        BitaxeDifficultySensor(coordinator, "bestSessionDiff", "Best Session Difficulty"),
        
        # Hardware metrics
        BitaxeTemperatureSensor(coordinator, "temp", "Chip Temperature"),
        BitaxeTemperatureSensor(coordinator, "vrTemp", "VR Temperature", False),
        BitaxeVoltageSensor(coordinator, "voltage", "Input Voltage"),
        BitaxeVoltageSensor(coordinator, "coreVoltageActual", "Core Voltage"),
        BitaxePowerSensor(coordinator, "power", "Power"),
        BitaxeCurrentSensor(coordinator, "current", "Current"),
        BitaxePercentageSensor(coordinator, "fanspeed", "Fan Speed"),
        BitaxeFanRpmSensor(coordinator, "fanrpm", "Fan RPM"),
        BitaxeFrequencySensor(coordinator, "frequency", "Frequency"),
        
        # System metrics
        BitaxeUptimeSensor(coordinator, "uptimeSeconds", "Uptime"),
        BitaxeWifiSensor(coordinator, "wifiRSSI", "WiFi Signal"),
        BitaxeMemorySensor(coordinator, "freeHeap", "Free Heap", False),
        BitaxeMemorySensor(coordinator, "freeHeapInternal", "Free Heap Internal", False),
        BitaxeMemorySensor(coordinator, "freeHeapSpiram", "Free Heap SPIRAM", False),
    ]

    async_add_entities(sensors)


class BitaxeSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Bitaxe sensors."""

    def __init__(
        self,
        coordinator: BitaxeDataUpdateCoordinator,
        key: str,
        name: str,
        enabled_default: bool = True,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.data.get('macAddr', 'unknown')}_{key}"
        self._attr_entity_registry_enabled_default = enabled_default
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.get("macAddr", "unknown"))},
            name=self.coordinator.name,
            manufacturer="Bitaxe",
            model=self.coordinator.data.get("ASICModel", "Unknown"),
            sw_version=self.coordinator.data.get("version", "Unknown"),
            configuration_url=f"http://{self.coordinator.data.get('ip', '')}",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)


class BitaxeHashrateSensor(BitaxeSensorBase):
    """Hashrate sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = GIGA_HASH_PER_SECOND
    _attr_icon = "mdi:chip"


class BitaxeSharesSensor(BitaxeSensorBase):
    """Shares sensor."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:counter"


class BitaxeDifficultySensor(BitaxeSensorBase):
    """Difficulty sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    @property
    def native_value(self):
        """Return the state of the sensor, converting string difficulty to float."""
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        
        # Handle string values like "39.2G", "27.4M", "1.5K"
        if isinstance(value, str):
            multipliers = {
                'K': 1_000,
                'M': 1_000_000,
                'G': 1_000_000_000,
                'T': 1_000_000_000_000,
            }
            
            # Try to extract the numeric part and suffix
            value_str = value.strip()
            if value_str and value_str[-1] in multipliers:
                try:
                    number = float(value_str[:-1])
                    return number * multipliers[value_str[-1]]
                except ValueError:
                    return None
            else:
                try:
                    return float(value_str)
                except ValueError:
                    return None
        
        return value


class BitaxePercentageSensor(BitaxeSensorBase):
    """Percentage sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:percent"


class BitaxeTemperatureSensor(BitaxeSensorBase):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class BitaxeVoltageSensor(BitaxeSensorBase):
    """Voltage sensor."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT


class BitaxePowerSensor(BitaxeSensorBase):
    """Power sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT


class BitaxeCurrentSensor(BitaxeSensorBase):
    """Current sensor."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE


class BitaxeFanRpmSensor(BitaxeSensorBase):
    """Fan RPM sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fan"
    _attr_native_unit_of_measurement = "RPM"


class BitaxeFrequencySensor(BitaxeSensorBase):
    """Frequency sensor."""

    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "MHz"
    _attr_icon = "mdi:sine-wave"


class BitaxeUptimeSensor(BitaxeSensorBase):
    """Uptime sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:clock-outline"


class BitaxeWifiSensor(BitaxeSensorBase):
    """WiFi signal sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_entity_registry_enabled_default = False


class BitaxeMemorySensor(BitaxeSensorBase):
    """Memory sensor."""

    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfInformation.BYTES
    _attr_icon = "mdi:memory"
    _attr_entity_registry_enabled_default = False
