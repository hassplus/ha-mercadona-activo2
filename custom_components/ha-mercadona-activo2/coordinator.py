"""Data coordinator for Activo2 integration."""
from datetime import timedelta
import logging
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.util import dt as dt_util
from datetime import datetime
from .lib.activo2 import Activo2API
from .lib.scheduleDTO import ScheduleResponse
from .lib.userinfoDTO import UserDTO

_LOGGER = logging.getLogger(__name__)

# Intervalo de actualización de datos
UPDATE_INTERVAL = timedelta(minutes=60)

def get_user_offset(cod_company):
    if cod_company == "08":
        timezone = ZoneInfo("Europe/Madrid")
    elif cod_company == "09":
        timezone = ZoneInfo("Europe/Lisbon")
    else:
        timezone = ZoneInfo("Europe/Madrid")
        _LOGGER.warning(f"Unknown company code: {cod_company}. Using Europe/Madrid as default.")

    # Get current time in the specified timezone
    now = datetime.now(timezone)

    # Format the offset
    offset = now.strftime("%z")
    # Convert from +0100 to +01:00 format
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"

    return offset


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
            user_info : UserDTO = await self.api.getUserInfo(self.id_token)

            # Get timezone and time offset from company
            user_offset = get_user_offset(user_info.cod_company)

            # Obtener datos completos del calendario
            schedule_data : ScheduleResponse = await self.api.getFullDaysData(self.id_token)

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
                                    start_time = f"{day.date}T{detail.schedule.start}:00{user_offset}"
                                    end_time = f"{day.date}T{detail.schedule.end}:00{user_offset}"

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
                                        task_start = f"{day.date}T{task.startHour}:00{user_offset}"
                                        task_end = f"{day.date}T{task.endHour}:00{user_offset}"

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
            data = {}
            data.update({'userinfo': user_info})
            data.update({
                'workshifts': workshifts,
                'tasks': tasks
            })

            return data

        except Exception as err:
            _LOGGER.exception("Error fetching Activo2 data: %s", err)
            raise

