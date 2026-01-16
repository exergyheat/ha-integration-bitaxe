"""Number platform for Bitaxe integration."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BitaxeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bitaxe number entities from a config entry."""
    coordinator: BitaxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers = [
        BitaxeCoreVoltageNumber(coordinator),
        BitaxeFrequencyNumber(coordinator),
        BitaxeFanSpeedNumber(coordinator),
        BitaxeTempTargetNumber(coordinator),
        BitaxeDisplayTimeoutNumber(coordinator),
        BitaxeStatsFrequencyNumber(coordinator),
    ]

    async_add_entities(numbers)


class BitaxeNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for Bitaxe number entities."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: BitaxeDataUpdateCoordinator,
        key: str,
        name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.data.get('macAddr', 'unknown')}_{key}"
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
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            await self.coordinator.api.update_settings({self._key: int(value)})
            await asyncio.sleep(5)  # Give device time to process
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self._key, value, err)


class BitaxeCoreVoltageNumber(BitaxeNumberBase):
    """Core voltage number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 1000
    _attr_native_max_value = 1400
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize core voltage number."""
        super().__init__(coordinator, "coreVoltage", "Core Voltage")


class BitaxeFrequencyNumber(BitaxeNumberBase):
    """Frequency number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 100
    _attr_native_max_value = 1000
    _attr_native_step = 25
    _attr_native_unit_of_measurement = "MHz"
    _attr_icon = "mdi:sine-wave"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize frequency number."""
        super().__init__(coordinator, "frequency", "Frequency")


class BitaxeFanSpeedNumber(BitaxeNumberBase):
    """Manual fan speed number entity."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize fan speed number."""
        super().__init__(coordinator, "fanspeed", "Fan Speed (Manual)")


class BitaxeTempTargetNumber(BitaxeNumberBase):
    """Temperature target number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 30
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize temperature target number."""
        super().__init__(coordinator, "temptarget", "Temperature Target")


class BitaxeDisplayTimeoutNumber(BitaxeNumberBase):
    """Display timeout number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = -1
    _attr_native_max_value = 240
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:monitor-off"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize display timeout number."""
        super().__init__(coordinator, "displayTimeout", "Display Timeout")


class BitaxeStatsFrequencyNumber(BitaxeNumberBase):
    """Statistics frequency number entity."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 600
    _attr_native_step = 30
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:chart-timeline-variant"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize stats frequency number."""
        super().__init__(coordinator, "statsFrequency", "Statistics Frequency")
