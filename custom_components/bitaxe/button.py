"""Button platform for Bitaxe integration."""
from __future__ import annotations

import asyncio
import logging

import aiohttp

from homeassistant.components.button import ButtonEntity
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
    """Set up Bitaxe button entities from a config entry."""
    coordinator: BitaxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    buttons = [
        BitaxeUpdateButton(coordinator),
        BitaxeRestartButton(coordinator),
        BitaxeIdentifyButton(coordinator),
    ]

    async_add_entities(buttons)


class BitaxeButtonBase(CoordinatorEntity, ButtonEntity):
    """Base class for Bitaxe button entities."""

    def __init__(
        self,
        coordinator: BitaxeDataUpdateCoordinator,
        key: str,
        name: str,
    ) -> None:
        """Initialize the button entity."""
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


class BitaxeUpdateButton(BitaxeButtonBase):
    """Manual update button entity."""

    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize update button."""
        super().__init__(coordinator, "update", "Update")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()


class BitaxeRestartButton(BitaxeButtonBase):
    """Restart button entity."""

    _attr_icon = "mdi:restart"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize restart button."""
        super().__init__(coordinator, "restart", "Restart")

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.api.restart()
            _LOGGER.info("Restart command sent to %s", self.coordinator.name)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            # Device may close connection before response is received - this is expected
            _LOGGER.info("Restart command sent to %s (device restarting)", self.coordinator.name)
        except Exception as err:
            _LOGGER.error("Failed to restart %s: %s", self.coordinator.name, err)


class BitaxeIdentifyButton(BitaxeButtonBase):
    """Identify button entity."""

    _attr_icon = "mdi:lightbulb-on"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: BitaxeDataUpdateCoordinator) -> None:
        """Initialize identify button."""
        super().__init__(coordinator, "identify", "Identify")

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.api.identify()
            _LOGGER.info("Identify command sent to %s", self.coordinator.name)
        except Exception as err:
            _LOGGER.error("Failed to identify %s: %s", self.coordinator.name, err)
