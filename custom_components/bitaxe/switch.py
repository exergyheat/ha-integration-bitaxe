"""Switch platform for Bitaxe integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up Bitaxe switch entities from a config entry."""
    coordinator: BitaxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        BitaxeAutoFanSwitch(coordinator),
        BitaxeOverclockSwitch(coordinator),
        BitaxeInvertScreenSwitch(coordinator),
    ]

    async_add_entities(switches)


class BitaxeSwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for Bitaxe switch entities."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: BitaxeDataUpdateCoordinator,
        key: str,
        name: str,
    ) -> None:
        """Initialize the switch entity."""
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
    def is_on(self) -> bool:
        """Return true if switch is on."""
        value = self.coordinator.data.get(self._key)
        return bool(value) if value is not None else False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.api.update_settings({self._key: 1})
            await asyncio.sleep(5)  # Give device time to process
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on %s: %s", self._key, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.api.update_settings({self._key: 0})
            await asyncio.sleep(5)  # Give device time to process
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off %s: %s", self._key, err)


class BitaxeAutoFanSwitch(BitaxeSwitchBase):
    """Auto fan speed switch entity."""

    _attr_icon = "mdi:fan-auto"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize auto fan switch."""
        super().__init__(coordinator, "autofanspeed", "Auto Fan Speed")


class BitaxeOverclockSwitch(BitaxeSwitchBase):
    """Overclock enabled switch entity."""

    _attr_icon = "mdi:speedometer"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize overclock switch."""
        super().__init__(coordinator, "overclockEnabled", "Overclock Enabled")


class BitaxeInvertScreenSwitch(BitaxeSwitchBase):
    """Invert screen switch entity."""

    _attr_icon = "mdi:invert-colors"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize invert screen switch."""
        super().__init__(coordinator, "invertscreen", "Invert Screen")
