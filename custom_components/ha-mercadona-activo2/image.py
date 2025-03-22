import logging
from typing import Optional

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import Activo2Coordinator
from .const import DOMAIN, SENSOR_PREFIX

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Activo2 image based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Add image entity
    async_add_entities([Activo2UserImageEntity(coordinator)])


class Activo2UserImageEntity(CoordinatorEntity, ImageEntity):
    """Implementation of an Activo2 image entity."""

    def __init__(self, coordinator: Activo2Coordinator) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator)
        self._attr_name = "Activo2 User Image"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{coordinator.username}_photo"
        self._attr_has_entity_name = True
        self._attr_content_type = "image/jpeg"
        self._image_url = None

    @property
    def access_tokens(self) -> list:
        """Return access tokens for the image, if any."""
        return [""]

    @property
    def image_url(self) -> Optional[str]:
        """Return the URL of the image."""
        if (
            self.coordinator.data
            and "userinfo" in self.coordinator.data
            and hasattr(self.coordinator.data["userinfo"], "photo")
        ):
            return self.coordinator.data["userinfo"].photo
        return None

    async def async_image(self) -> bytes:
        """Return bytes of image."""
        if not self.image_url:
            return b""

        session = self.coordinator.session

        try:
            async with session.get(self.image_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    _LOGGER.error(
                        "Error fetching image from %s. Status: %s",
                        self.image_url,
                        response.status,
                    )
                    return b""
        except Exception as err:
            _LOGGER.exception("Error fetching image: %s", err)
            return b""
