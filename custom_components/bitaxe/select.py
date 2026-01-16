"""Select platform for Bitaxe integration."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ROTATION_OPTIONS
from .coordinator import BitaxeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bitaxe select entities from a config entry."""
    coordinator: BitaxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    selects = [
        BitaxeRotationSelect(coordinator),
    ]

    async_add_entities(selects)


class BitaxeSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for Bitaxe select entities."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: BitaxeDataUpdateCoordinator,
        key: str,
        name: str,
        options_map: dict[str, int],
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._key = key
        self._options_map = options_map
        self._reverse_map = {v: k for k, v in options_map.items()}
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.data.get('macAddr', 'unknown')}_{key}"
        self._attr_options = list(options_map.keys())
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
    def current_option(self) -> str | None:
        """Return the current option."""
        value = self.coordinator.data.get(self._key)
        return self._reverse_map.get(value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = self._options_map.get(option)
        if value is None:
            _LOGGER.error("Invalid option %s for %s", option, self._key)
            return

        try:
            await self.coordinator.api.update_settings({self._key: value})
            await asyncio.sleep(5)  # Give device time to process
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self._key, option, err)


class BitaxeRotationSelect(BitaxeSelectBase):
    """Screen rotation select entity."""

    _attr_icon = "mdi:screen-rotation"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize rotation select."""
        super().__init__(coordinator, "rotation", "Screen Rotation", ROTATION_OPTIONS)
