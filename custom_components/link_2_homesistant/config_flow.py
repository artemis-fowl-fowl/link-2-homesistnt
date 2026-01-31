"""Config flow for Link 2 Home Assistant."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

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


class Link2HomeAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Link 2 Home Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            if not user_input[CONF_REMOTE_URL].startswith(("http://", "https://")):
                errors[CONF_REMOTE_URL] = "invalid_url"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.selector(
                    {"text": {"type": "text"}}
                ),
                vol.Required(CONF_REMOTE_URL): selector.selector(
                    {"text": {"type": "url"}}
                ),
                vol.Required(CONF_REMOTE_TOKEN): selector.selector(
                    {"text": {"type": "password"}}
                ),
                vol.Required(CONF_REMOTE_ENTITY_ID): selector.selector(
                    {"text": {"type": "text"}}
                ),
                vol.Optional(CONF_SOURCE_ENTITY_ID): selector.selector(
                    {"entity": {"domain": "switch"}}
                ),
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=DEFAULT_POLL_INTERVAL,
                ): selector.selector(
                    {
                        "number": {
                            "min": 1,
                            "max": 3600,
                            "step": 1,
                            "mode": "box",
                            "unit_of_measurement": "s",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return Link2HomeAssistantOptionsFlow(config_entry)


class Link2HomeAssistantOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._config_entry.data, **self._config_entry.options}

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=current.get(CONF_NAME, DEFAULT_NAME),
                ): selector.selector(
                    {"text": {"type": "text"}}
                ),
                vol.Required(CONF_REMOTE_URL, default=current.get(CONF_REMOTE_URL, "")): selector.selector(
                    {"text": {"type": "url"}}
                ),
                vol.Required(CONF_REMOTE_TOKEN, default=current.get(CONF_REMOTE_TOKEN, "")): selector.selector(
                    {"text": {"type": "password"}}
                ),
                vol.Required(
                    CONF_REMOTE_ENTITY_ID,
                    default=current.get(CONF_REMOTE_ENTITY_ID, ""),
                ): selector.selector({"text": {"type": "text"}}),
                vol.Optional(
                    CONF_SOURCE_ENTITY_ID,
                    default=current.get(CONF_SOURCE_ENTITY_ID),
                ): selector.selector({"entity": {"domain": "switch"}}),
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): selector.selector(
                    {
                        "number": {
                            "min": 1,
                            "max": 3600,
                            "step": 1,
                            "mode": "box",
                            "unit_of_measurement": "s",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
