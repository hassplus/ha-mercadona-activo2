"""Data coordinator for Activo2 integration."""
from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.util import dt as dt_util
from .lib.activo2 import Activo2API

_LOGGER = logging.getLogger(__name__)

# Intervalo de actualización de datos
UPDATE_INTERVAL = timedelta(minutes=60)


class Activo2Coordinator(DataUpdateCoordinator):
    """Coordinator to manage Activo2 data updates."""

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Activo2",
            update_interval=UPDATE_INTERVAL,
        )

        self.username = username
        self.password = password
        self.session = async_create_clientsession(hass)
        self.api = Activo2API(self.session)
        self.id_token = None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Iniciar sesión para obtener token
            self.id_token = await self.api.login(self.username, self.password)

            if self.id_token is None:
                raise ConfigEntryAuthFailed("Failed to authenticate with Activo2 with username = " + self.username)

            # Obtener información del usuario
            user_info = await self.api.getUserInfo(self.id_token)

            # Obtener datos completos del calendario
            schedule_data = await self.api.getFullDaysData(self.id_token)

            # Procesar los datos del calendario para adaptarlos al formato de calendario
            workshifts = []
            tasks = []

            if schedule_data and schedule_data.months:
                for month in schedule_data.months:
                    for week in month.weeks:
                        for day in week.days:
                            if day.hasTasks and day.detail:
                                for detail in day.detail:
                                    # Procesar el horario general
                                    # Ensure date format is ISO 8601 with timezone
                                    start_time = f"{day.date}T{detail.schedule.start}:00+00:00"
                                    end_time = f"{day.date}T{detail.schedule.end}:00+00:00"

                                    # Crear evento para el turno completo
                                    workshifts.append({
                                        "uid": f"workshift_{day.date}",
                                        "summary": f"Turno en {detail.store.name}",
                                        "start": start_time,
                                        "end": end_time,
                                        "location": f"{detail.store.codeLabel} - {detail.store.name}",
                                        "description": f"Turno de trabajo: {detail.schedule.total} horas",
                                        "night_shift": detail.schedule.nightShift,
                                        "night_shift_label": detail.schedule.nightShiftLabel
                                    })

                                    # Procesar tareas individuales
                                    for task in detail.taskList:
                                        # Ensure date format is ISO 8601 with timezone
                                        task_start = f"{day.date}T{task.startHour}:00+00:00"
                                        task_end = f"{day.date}T{task.endHour}:00+00:00"

                                        tasks.append({
                                            "uid": f"task_{day.date}_{task.processId}",
                                            "summary": task.name,
                                            "start": task_start,
                                            "end": task_end,
                                            "location": f"{detail.store.codeLabel} - {detail.store.name}",
                                            "description": task.description,
                                            "color": task.colour,
                                            "priority": task.priority
                                        })

            # Combinar datos
            data = user_info if user_info else {}
            data.update({
                'workshifts': workshifts,
                'tasks': tasks
            })

            return data

        except Exception as err:
            _LOGGER.exception("Error fetching Activo2 data: %s", err)
            raise