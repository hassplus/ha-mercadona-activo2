"""Plataforma calendar para la integración de Activo2 (eventos de calendario)."""
from __future__ import annotations
import logging
from typing import List
from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SENSOR_PREFIX
from .coordinator import Activo2Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura las entidades de calendario para Activo2."""
    coordinator: Activo2Coordinator = hass.data[DOMAIN][entry.entry_id]
    username = entry.data["username"]

    entities = [
        Activo2WorkshiftCalendarEntity(coordinator, username),
        Activo2TasksCalendarEntity(coordinator, username),
    ]
    async_add_entities(entities)

class Activo2WorkshiftCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Entidad de calendario para los turnos de trabajo de Activo2."""
    def __init__(self, coordinator: Activo2Coordinator, username: str) -> None:
        super().__init__(coordinator)
        self._username = username
        self._attr_name = f"{SENSOR_PREFIX} {username} Work Shifts"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{username}_workshifts"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "workshifts" in self.coordinator.data
        )

    @property
    def native_event(self) -> CalendarEvent | None:
        if not self.available:
            return None

        now = dt_util.now()
        for event in self.coordinator.data["workshifts"]:
            event_start = dt_util.as_utc(dt_util.parse_datetime(event["start"]))
            event_end = dt_util.as_utc(dt_util.parse_datetime(event["end"]))
            if event_start <= now <= event_end:
                return CalendarEvent(
                    start=event_start,
                    end=event_end,
                    summary=event["summary"],
                    description=event.get("description", ""),
                    location=event.get("location", ""),
                    uid=event["uid"],
                )
        return None

    @property
    def event(self) -> CalendarEvent | None:
        """Soporte legacy: devuelve el evento actual."""
        return self.native_event

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Devuelve eventos dentro de un rango de fechas."""
        if not self.available:
            return []

        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)
        events = []
        for event in self.coordinator.data["workshifts"]:
            event_start = dt_util.as_utc(dt_util.parse_datetime(event["start"]))
            event_end = dt_util.as_utc(dt_util.parse_datetime(event["end"]))
            if event_start <= end_date and event_end >= start_date:
                events.append(
                    CalendarEvent(
                        start=event_start,
                        end=event_end,
                        summary=event["summary"],
                        description=event.get("description", ""),
                        location=event.get("location", ""),
                        uid=event["uid"],
                    )
                )
        return events

class Activo2TasksCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Entidad de calendario para las tareas de Activo2."""
    def __init__(self, coordinator: Activo2Coordinator, username: str) -> None:
        super().__init__(coordinator)
        self._username = username
        self._attr_name = f"{SENSOR_PREFIX} {username} Tasks"
        self._attr_unique_id = f"{SENSOR_PREFIX}_{username}_tasks"
        self._attr_icon = "mdi:calendar-check"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "tasks" in self.coordinator.data
        )

    @property
    def native_event(self) -> CalendarEvent | None:
        if not self.available:
            return None

        now = dt_util.now()
        for event in self.coordinator.data["tasks"]:
            event_start = dt_util.as_utc(dt_util.parse_datetime(event["start"]))
            event_end = dt_util.as_utc(dt_util.parse_datetime(event["end"]))
            if event_start <= now <= event_end:
                return CalendarEvent(
                    start=event_start,
                    end=event_end,
                    summary=event["summary"],
                    description=event.get("description", ""),
                    location=event.get("location", ""),
                    uid=event["uid"],
                )
        return None

    @property
    def event(self) -> CalendarEvent | None:
        return self.native_event

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Devuelve eventos dentro de un rango de fechas."""
        if not self.available:
            return []

        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)
        events = []
        for event in self.coordinator.data["tasks"]:
            event_start = dt_util.as_utc(dt_util.parse_datetime(event["start"]))
            event_end = dt_util.as_utc(dt_util.parse_datetime(event["end"]))
            if event_start <= end_date and event_end >= start_date:
                events.append(
                    CalendarEvent(
                        start=event_start,
                        end=event_end,
                        summary=event["summary"],
                        description=event.get("description", ""),
                        location=event.get("location", ""),
                        uid=event["uid"],
                    )
                )
        return events
