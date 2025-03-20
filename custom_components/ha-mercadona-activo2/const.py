"""Constants for the Detailed Hello World Push integration."""
from homeassistant.const import Platform

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "ha-mercadona-activo2"
SENSOR_PREFIX = 'activo2'
# Plataformas soportadas
PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]