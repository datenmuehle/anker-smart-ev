import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT
from .hub import AnkerSolixHub

class AnkerSolixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Anker SOLIX EV Charger."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            hub = AnkerSolixHub(host, port)
            
            if await hub.connect():
                hub.disconnect()
                return self.async_create_entry(title=user_input.get(CONF_NAME, DEFAULT_NAME), data=user_input)
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }),
            errors=errors,
        )
