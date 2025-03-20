"""Integración de Activo2 para Home Assistant."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, PLATFORMS
from .coordinator import Activo2Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration from YAML (no recomendado)."""
    _LOGGER.debug("Setting up integration from YAML")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from una entrada de configuración."""
    _LOGGER.debug("Setting up config entry %s", entry.entry_id)

    # Crear el coordinador de forma centralizada
    username = entry.data["username"]
    password = entry.data["password"]
    coordinator = Activo2Coordinator(hass, username, password)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Reenviar la configuración a las plataformas definidas
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Desmonta una entrada de configuración."""
    _LOGGER.debug("Unloading config entry %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
