"""The config_flow for APsystems local API integration."""

from typing import Any

from aiohttp.client_exceptions import ClientConnectionError

from homeassistant.helpers.storage import Store
from .APsystemsEZ1 import APsystemsEZ1M
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_PORT, DOMAIN, UPDATE_INTERVAL, BASE_PRODUCED_P1, BASE_PRODUCED_P2

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(UPDATE_INTERVAL, default=15): int,
        vol.Optional(BASE_PRODUCED_P1): float,
        vol.Optional(BASE_PRODUCED_P2): float
    }
)


class APsystemsLocalAPIFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Apsystems local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass, False)
            api = APsystemsEZ1M(
                ip_address=user_input[CONF_IP_ADDRESS],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                session=session,
            )
            try:
                device_info = await api.get_device_info()
            except (TimeoutError, ClientConnectionError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(device_info.deviceId)
                self._abort_if_unique_id_configured()

                # from info: Store is now a Generic class: self._store = Store[dict[str, int]](hass, STORAGE_VERSION, STORAGE_KEY)
                _store = Store[dict[str, float]](self.hass, 1, f"{DOMAIN}_storage_{device_info.deviceId}")
                _sData = await _store.async_load()
                if _sData is not None:
                    _sData =  {
                        # use stored values if no user input, however user input always overwrites stored values
                        BASE_PRODUCED_P1: user_input.get(BASE_PRODUCED_P1, _sData.get(BASE_PRODUCED_P1, 0)),
                        BASE_PRODUCED_P2: user_input.get(BASE_PRODUCED_P2, _sData.get(BASE_PRODUCED_P2, 0))
                    }
                else:
                    _sData =  {
                        BASE_PRODUCED_P1: user_input.get(BASE_PRODUCED_P1, 0),
                        BASE_PRODUCED_P2: user_input.get(BASE_PRODUCED_P2, 0)
                    }
                await _store.async_save(_sData)

                return self.async_create_entry(
                    title="Solar",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfigure step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass, False)
            api = APsystemsEZ1M(
                ip_address=user_input[CONF_IP_ADDRESS],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                session=session,
            )
            try:
                device_info = await api.get_device_info()
            except (TimeoutError, ClientConnectionError):
                errors["base"] = "cannot_connect"
            else:
                # await self.async_set_unique_id(device_info.deviceId)

                # from info: Store is now a Generic class: self._store = Store[dict[str, int]](hass, STORAGE_VERSION, STORAGE_KEY)
                _store = Store[dict[str, float]](self.hass, 1, f"{DOMAIN}_storage_{device_info.deviceId}")
                _sData = await _store.async_load()
                if _sData is not None:
                    _sData =  {
                        # use stored values if no user input, however user input always overwrites stored values
                        BASE_PRODUCED_P1: user_input.get(BASE_PRODUCED_P1, _sData.get(BASE_PRODUCED_P1, 0)),
                        BASE_PRODUCED_P2: user_input.get(BASE_PRODUCED_P2, _sData.get(BASE_PRODUCED_P2, 0))
                    }
                else:
                    _sData =  {
                        BASE_PRODUCED_P1: user_input.get(BASE_PRODUCED_P1, 0),
                        BASE_PRODUCED_P2: user_input.get(BASE_PRODUCED_P2, 0)
                    }
                await _store.async_save(_sData)

                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )