"""Constants for the APsystems Local API integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
DOMAIN = "apsystemsapi_local"
DEFAULT_PORT = 8050
UPDATE_INTERVAL = "update_interval"
BASE_PRODUCED_P1 = "base_produced_p1"
BASE_PRODUCED_P2 = "base_produced_p2"
