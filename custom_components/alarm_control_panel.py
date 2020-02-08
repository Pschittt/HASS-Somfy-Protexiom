import configparser
from .somfy import Somfy
import logging

from datetime import timedelta
import logging

import voluptuous as vol

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    # SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMED,
)

from . import DOMAIN as SOMFY_DOMAIN

DEFAULT_ALARM_NAME = "Somfy Protexiom Alarm"
ACTIVATION_ALARM_CODE = None
ALARM_STATE = None

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    alarms = []

    controller = hass.data[SOMFY_DOMAIN]["controller"]

    alarms.append(SomfyAlarm(hass, controller))
    add_entities(alarms)


def set_arm_state(state, hass, somfy, code=None):
    """Send set arm state command."""
    _LOGGER.debug("Somfy set arm state %s", state)
    ACTIVATION_ALARM_CODE = hass.data[SOMFY_DOMAIN]["activation_alarm_code"]

    if ACTIVATION_ALARM_CODE is not None and code != ACTIVATION_ALARM_CODE:
        _LOGGER.debug("Wrong activation code %s and %s", code, ACTIVATION_ALARM_CODE)
        return

    try: 
        somfy.login()
        if state.lower() == STATE_ALARM_DISARMED.lower():
            _activate_result = somfy.unset_all_zone()
            _LOGGER.debug("Somfy protexiom desactivate alarm") 
        elif state.lower() == STATE_ALARM_ARMED_AWAY.lower():
            _LOGGER.debug("Somfy protexiom alarm activation") 
            _activate_result = somfy.set_all_zone()
        else:
            _LOGGER.debug("No match")
    except:
        _LOGGER.debug("Somfy could not activate alarm")
        _LOGGER.debug("Error when trying to log in")
    try:    
        _state_result = somfy.get_state()
        _LOGGER.debug("state")
        _LOGGER.debug(_state_result)
    except:
        _LOGGER.debug("Error when trying to get state")    
    try:
        somfy.logout()
        hass.data[SOMFY_DOMAIN]["state"] = _state_result
    except:
        _LOGGER.debug("Error when trying to log out !")


class SomfyAlarm(alarm.AlarmControlPanel):

    def __init__(self, hass, controller):
        self._state = None
        self.somfy = controller
        self._hass = hass
        self._changed_by = None

    @property
    def name(self):
        """Return the name of the device."""
        return DEFAULT_ALARM_NAME

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_AWAY

    @property
    def code_format(self):
        """Return one or more digits/characters."""
        return alarm.FORMAT_NUMBER

    @property
    def changed_by(self):
        """Return the last change triggered by."""
        return self._changed_by

    def update(self):
        """Update alarm status."""
        state = self._hass.data[SOMFY_DOMAIN]["state"]
        if state['alarm'] == "Pas d'alarme" :
            self._state = STATE_ALARM_DISARMED
        else:
            self._state = STATE_ALARM_ARMED_AWAY
        _LOGGER.debug("State alarm %s ", self._state)
        
    def alarm_disarm(self, code=None):
        """Send disarm command."""
        set_arm_state("DISARMED", self._hass, self.somfy, code)

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        set_arm_state("ARMED_HOME", self._hass, self.somfy, code)

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        set_arm_state("ARMED_AWAY", self._hass, self.somfy, code)
