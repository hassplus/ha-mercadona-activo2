"""Plataforma sensor para la integración de Activo2 (información de usuario)."""
from __future__ import annotations
import logging
from typing import Final
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_PREFIX
from .coordinator import Activo2Coordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES_USERINFO: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        key="userid",
        name="User Id",
        icon="mdi:card-account-details-outline",
    ),
    SensorEntityDescription(
        key="fullname",
        name="Full name",
        icon="mdi:account",
    ),
    SensorEntityDescription(
        key="photourl",
        name="Photo Url",
        icon="mdi:image",
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura los sensores de información de usuario."""
    coordinator: Activo2Coordinator = hass.data[DOMAIN][entry.entry_id]
    username = entry.data["username"]

    entities = []
    for description in SENSOR_TYPES_USERINFO:
        entities.append(Activo2UserInfoEntity(coordinator, description, username))
    async_add_entities(entities)

class Activo2UserInfoEntity(CoordinatorEntity, SensorEntity):
    """Representa un sensor con la información del usuario de Activo2."""
    def __init__(
        self,
        coordinator: Activo2Coordinator,
        description: SensorEntityDescription,
        username: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._username = username
        self._attr_name = f"{SENSOR_PREFIX} {username} {description.name}"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{username}_{description.key}"
        self._attr_icon = description.icon

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def native_value(self):
        if not self.available or self.entity_description.key not in self.coordinator.data:
            return None
        return self.coordinator.data[self.entity_description.key]

    @property
    def entity_picture(self):
        if (
            self.entity_description.key == "photourl"
            and self.coordinator.data
            and "photourl" in self.coordinator.data
        ):
            return self.coordinator.data["photourl"]
        return None
