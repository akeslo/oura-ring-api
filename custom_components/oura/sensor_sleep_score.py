"""Proivdes a sleep score sensor."""

import logging
import voluptuous as vol
from homeassistant import const
from homeassistant.helpers import config_validation as cv
from . import api
from . import sensor_base

# Sensor configuration
_DEFAULT_NAME = 'oura_sleep_score'

CONF_KEY_NAME = 'sleep_score'
_DEFAULT_MONITORED_VARIABLES = [
    'day',
    'score',
]
_SUPPORTED_MONITORED_VARIABLES = [
    'day',
    'deep_sleep',
    'efficiency',
    'latency',
    'rem_sleep',
    'restfulness',
    'score',
    'timing',
    'timestamp',
    'total_sleep',
]

CONF_SCHEMA = {
    vol.Optional(const.CONF_NAME, default=_DEFAULT_NAME): cv.string,

    vol.Optional(
        sensor_base.CONF_MONITORED_DATES,
        default=sensor_base.DEFAULT_MONITORED_DATES
    ): cv.ensure_list,

    vol.Optional(
        const.CONF_MONITORED_VARIABLES,
        default=_DEFAULT_MONITORED_VARIABLES
    ): vol.All(cv.ensure_list, [vol.In(_SUPPORTED_MONITORED_VARIABLES)]),

    vol.Optional(
        sensor_base.CONF_BACKFILL,
        default=sensor_base.DEFAULT_BACKFILL
    ): cv.positive_int,
}

# There is no need to add any configuration as all fields are optional and
# with default values. However, this is done as it is used in the main sensor.
DEFAULT_CONFIG = {}

_EMPTY_SENSOR_ATTRIBUTE = {
    variable: None for variable in _SUPPORTED_MONITORED_VARIABLES
}


class OuraSleepScoreSensor(sensor_base.OuraDatedSensor):
  """Representation of an Oura Ring Sleep Score sensor.

  Attributes:
    name: name of the sensor.
    state: state of the sensor.
    extra_state_attributes: attributes of the sensor.

  Methods:
    async_update: updates sensor data.
  """

  def __init__(self, config, hass):
    """Initializes the sensor."""
    sleep_score_config = (
        config.get(const.CONF_SENSORS, {}).get(CONF_KEY_NAME, {}))
    super(OuraSleepScoreSensor, self).__init__(
        config, hass, sleep_score_config)

    self._api_endpoint = api.OuraEndpoints.SLEEP_SCORE
    self._empty_sensor = _EMPTY_SENSOR_ATTRIBUTE
    self._main_state_attribute = 'score'

  def parse_sensor_data(self, oura_data):
    """Processes sleep score data into a dictionary.

    Args:
      oura_data: Sleep Score (Daily Sleep) data in list format from Oura API.

    Returns:
      Dictionary where key is the requested summary_date and value is the
      Oura sleep score data for that given day.
    """
    if not oura_data or 'data' not in oura_data:
      logging.error(
          f'Oura ({self._name}): Couldn\'t fetch data for Oura ring sensor.')
      return {}

    sleep_score_data = oura_data.get('data')
    if not sleep_score_data:
      return {}

    sleep_score_dict = {}
    for sleep_score_daily_data in sleep_score_data:
      # Default metrics.
      sleep_score_date = sleep_score_daily_data.get('day')
      if not sleep_score_date:
        continue

      contributors = sleep_score_daily_data.get('contributors', {})
      sleep_score_daily_data.update(contributors)
      del sleep_score_daily_data['contributors']

      sleep_score_dict[sleep_score_date] = sleep_score_daily_data

    return sleep_score_dict
