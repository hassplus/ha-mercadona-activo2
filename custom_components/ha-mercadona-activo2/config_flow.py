from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from .const import DOMAIN  # pylint:disable=unused-import
from .lib.activo2 import *
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.data_entry_flow import FlowHandler, FlowResult
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD
)

_LOGGER = logging.getLogger(__name__)

# Schema para la configuración del usuario
USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})


class Activo2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow para múltiples cuentas Activo2."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()

    async def async_step_user(self, user_input=None):
        """Maneja el paso de entrada de usuario."""
        errors = {}
        if user_input is not None:
            try:
                # Validar credenciales
                is_valid = await self.validate_input(self.hass, user_input)

                if is_valid:
                    # Usar el nombre de usuario como identificador único
                    username = user_input[CONF_USERNAME]

                    # Verificar si ya existe una entrada con este usuario
                    await self.async_set_unique_id(f"{DOMAIN}_{username}")
                    self._abort_if_unique_id_configured()

                    # Crear la entrada de configuración usando el nombre de usuario como título
                    return self.async_create_entry(
                        title=username,
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: user_input[CONF_PASSWORD]
                        }
                    )
                else:
                    errors['username'] = 'wrong_credentials'
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Si no hay entrada de usuario o hubo errores, mostrar el formulario nuevamente
        return self.async_show_form(
            step_id="user",
            data_schema=USER_DATA_SCHEMA,
            errors=errors
        )

    async def validate_input(self, hass: HomeAssistant, data: dict) -> bool:
        """Valida las credenciales de usuario.

        Data tiene las claves de USER_DATA_SCHEMA con valores proporcionados por el usuario.
        """
        session = async_create_clientsession(hass)
        api = Activo2API(session)
        try:
            id_token = await api.login(data[CONF_USERNAME], data[CONF_PASSWORD])
            if id_token is not None:
                return True
            else:
                raise InvalidAuth
        except Exception as exception:
            _LOGGER.error(f"Error al conectar con Activo2: {exception}")
            raise CannotConnect from exception


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""