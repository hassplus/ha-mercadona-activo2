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
from .lib.userinfoDTO import UserDTO

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES_USERINFO: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        key="user",
        name="User Info",
        icon="mdi:card-account-details-outline",
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura los sensores de información de usuario."""
    coordinator: Activo2Coordinator = hass.data[DOMAIN][entry.entry_id]
    user_info : UserDTO = coordinator.data["userinfo"]

    entities = []
    for description in SENSOR_TYPES_USERINFO:
        entities.append(Activo2UserInfoEntity(coordinator, description, user_info.userid))
    async_add_entities(entities)

class Activo2UserInfoEntity(CoordinatorEntity, SensorEntity):
    """Representa un sensor con la información del usuario de Activo2."""
    def __init__(
        self,
        coordinator: Activo2Coordinator,
        description: SensorEntityDescription,
        userid: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._username = userid
        self._attr_name = f"{SENSOR_PREFIX} {userid} {description.name}"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{userid}_{description.key}"
        self._attr_icon = description.icon

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def native_value(self):
        if not self.available:
            return None
        user_info : UserDTO = self.coordinator.data["userinfo"]
        return f"{user_info.name} {user_info.lastname}"

    @property
    def entity_picture(self):
        if self.available:
            user_info: UserDTO = self.coordinator.data["userinfo"]
            return user_info.photo
        return None

    @property
    def extra_state_attributes(self):
        if not self.available:
            return None

        user_info: UserDTO = self.coordinator.data["userinfo"]
        employee_number = None
        if hasattr(user_info, "companies") and user_info.companies:
            for company in user_info.companies:
                if company.active:
                    employee_number = company.employee_number
                    break

        return {
            "userid": user_info.userid,
            "name": user_info.name,
            "lastname": user_info.lastname,
            "email": user_info.email,
            "photo": user_info.photo,
            "company": user_info.company,
            "department": user_info.department,
            "region": user_info.region,
            "division_zone": user_info.division_zone,
            "cod_store": user_info.cod_store,
            "store": user_info.store,
            "employee_number": employee_number,
        }