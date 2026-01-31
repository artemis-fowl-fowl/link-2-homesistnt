"""Switch platform for Link 2 Home Assistant."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    CONF_NAME,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval

from .const import (
    CONF_POLL_INTERVAL,
    CONF_REMOTE_ENTITY_ID,
    CONF_REMOTE_TOKEN,
    CONF_REMOTE_URL,
    CONF_SOURCE_ENTITY_ID,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_REMOTE_URL): cv.url,
        vol.Required(CONF_REMOTE_TOKEN): cv.string,
        vol.Required(CONF_REMOTE_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_SOURCE_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): cv.positive_int,
    }
)


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    """Set up the Link 2 Home Assistant switch platform."""
    entity = LinkedSwitch(hass, config)
    async_add_entities([entity], update_before_add=True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the switch from a config entry."""
    config = {**entry.data, **entry.options}
    entity = LinkedSwitch(hass, config, unique_id=entry.entry_id)
    async_add_entities([entity], update_before_add=True)


class LinkedSwitch(SwitchEntity):
    """Representation of a linked remote switch."""

    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, config, unique_id: str | None = None) -> None:
        self.hass = hass
        self._name = config.get(CONF_NAME, DEFAULT_NAME)
        self._remote_url = config[CONF_REMOTE_URL].rstrip("/")
        self._remote_token = config[CONF_REMOTE_TOKEN]
        self._remote_entity_id = config[CONF_REMOTE_ENTITY_ID]
        self._source_entity_id = config.get(CONF_SOURCE_ENTITY_ID)
        self._poll_interval = timedelta(seconds=config.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        self._is_on: bool | None = None
        self._session = aiohttp_client.async_get_clientsession(hass)
        self._unsub_poll = None
        self._lock = asyncio.Lock()
        if unique_id:
            self._attr_unique_id = unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_added_to_hass(self) -> None:
        if self._source_entity_id:
            unsub_source = async_track_state_change_event(
                self.hass,
                [self._source_entity_id],
                self._handle_source_change,
            )
            self.async_on_remove(unsub_source)

        self._unsub_poll = async_track_time_interval(
            self.hass,
            self._handle_poll,
            self._poll_interval,
        )
        self.async_on_remove(self._unsub_poll)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_poll:
            self._unsub_poll()
            self._unsub_poll = None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._call_remote(True)
        await self.async_update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._call_remote(False)
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch state from remote Home Assistant."""
        async with self._lock:
            state = await self._fetch_remote_state()
            if state is None:
                return
            self._is_on = state == STATE_ON

    async def _fetch_remote_state(self) -> str | None:
        url = f"{self._remote_url}/api/states/{self._remote_entity_id}"
        headers = {"Authorization": f"Bearer {self._remote_token}"}
        try:
            async with self._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("state")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    async def _call_remote(self, turn_on: bool) -> None:
        service = "turn_on" if turn_on else "turn_off"
        url = f"{self._remote_url}/api/services/switch/{service}"
        headers = {
            "Authorization": f"Bearer {self._remote_token}",
            "Content-Type": "application/json",
        }
        payload = {"entity_id": self._remote_entity_id}
        async with self._lock:
            try:
                async with self._session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    await resp.text()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                return

    @callback
    async def _handle_source_change(self, event) -> None:
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        if new_state.state == STATE_ON:
            await self._call_remote(True)
        elif new_state.state == STATE_OFF:
            await self._call_remote(False)

    async def _handle_poll(self, _now) -> None:
        await self.async_update()
        self.async_write_ha_state()
