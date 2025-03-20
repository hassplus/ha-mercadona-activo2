from datetime import date, timedelta
import logging
from .const import *
from .dto import ScheduleResponse

_LOGGER = logging.getLogger(__name__)

class Activo2API(object):
    def __init__(self, session):
        self._session = session

    # return id_token to call API
    async def login(self, username, password):
        # Realiza la solicitud para obtener el id_token
        response_token = await self._session.post(OAUTH2_TOKEN_URL, data={
            "grant_type": OAUTH2_GRANT_TYPE,
            "username": USERNAME_PREFIX + username,
            "password": password,
            "client_id": OAUTH2_CLIENT_ID,
            "scope": OAUTH2_SCOPE,
            "response_type": OAUTH2_RESPONSE_TYPE
        }, headers=self._generateHeaders(None))
        # _LOGGER.debug(response_token)
        if response_token.status != 200:
            _LOGGER.error("Error login. Status: " + str(
                response_token.status) + ". Response body: " + await response_token.text())
            return None

        # Extrae el id_token de la respuesta
        json = await response_token.json()
        return json.get("id_token")

    # ----------------------------------------------------------------

    def _generateHeaders(self, id_token):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Language": "es",
            "Accept": "application/json, text/plain, */*",
            "App-Version": "3.16.0",
            "Referer": "https://activo2.mercadona.com/",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
        }
        if id_token is not None:
            headers.update({"Authorization": f"Bearer {id_token}"})
        return headers

    async def getUserInfo(self, id_token):
        response_api = await self._session.post(API_URL_USERINFO, headers=self._generateHeaders(id_token))
        _LOGGER.debug(response_api)
        if response_api.status == 200:
            json = await response_api.json()
            userid = json["userid"]
            fullname = json["name"] + " " + json["lastname"]
            photo = json["photo"]
            return {"userid": userid, "fullname": fullname, "photourl": photo}
        else:
            _LOGGER.error(f"Error calling API: {response_api.status}. Body: {await response_api.text()}")
            return None

    # -----------------------

    async def getFullDaysData(self, id_token) -> ScheduleResponse:
        response_api = await self._session.get(API_URL_SCHEDULE, headers=self._generateHeaders(id_token))
        _LOGGER.debug(response_api)

        # Procesa la respuesta de la API
        if response_api.status == 200:
            api_json = await response_api.json()
            # Convertimos el JSON recibido a una instancia del DTO ScheduleResponse
            return ScheduleResponse(**api_json)
        else:
            _LOGGER.error(f"Error calling API: {response_api.status}. Body: {await response_api.text()}")

        return ScheduleResponse()