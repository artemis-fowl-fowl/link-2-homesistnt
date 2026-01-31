"""Link 2 Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
	"""Set up the integration from YAML (legacy)."""
	return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""Set up Link 2 Home Assistant from a config entry."""
	await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
	return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""Unload a config entry."""
	return await hass.config_entries.async_unload_platforms(entry, ["switch"])
