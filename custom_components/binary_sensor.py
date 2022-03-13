import configparser
from .somfy import Somfy
import logging

from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import *
from homeassistant.const import (
    STATE_OFF, 
    STATE_ON,
)

from . import DOMAIN as SOMFY_DOMAIN
from .const import *

_LOGGER = logging.getLogger(__name__)

DEFAULT_DEVICE_CLASS = "None"
DEFAULT_BINARY_SENSOR_NAME = "somfy_binary_state"

SCAN_INTERVAL = timedelta(minutes=1)

def setup_platform(hass, config, add_entities, discovery_info=None):
    _hass = hass
    controller = hass.data[SOMFY_DOMAIN]["controller"]
    somfy_devices = []
    for device, deviceTypeList in hass.data[SOMFY_DOMAIN]["devices"].items():
        for deviceType in deviceTypeList:
            somfy_devices.append(SomfyBinarySensor(hass, controller, device, deviceType))
    add_entities(somfy_devices, True)


class SomfyBinarySensor(BinarySensorDeviceEntity):

    def __init__(self, hass, somfy, somfy_device, deviceType):
        self.somfy = somfy
        self._attributes = {}
        self._state = None
        self._state_attr = {}
        self._hass = hass
        self._device = somfy_device
        self._name = "somfy_"+self._device+"_"+SENSOR_TYPES[deviceType][0]
        self._fname = ""
        self._deviceType = deviceType
        self._device_class = SENSOR_TYPES[deviceType][3]
        self._icon = SENSOR_TYPES[deviceType][2]
        _LOGGER.debug("_device %s, _name %s, _device_class %s" % (self._device, self._name, self._device_class))

    @property
    def name(self):
        return self._name

    @property
    def friendly_name(self):
        return self._fname

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon
    
    @property
    def device_class(self):
        """Return the class of this sensor, from DEVICE_CLASSES."""
        return self._device_class

    @property
    def device_state_attributes(self):
        _LOGGER.debug(self._state_attr)
        return self._state_attr

    def update(self):
        _LOGGER.debug("########## UPDATING ######################")
        state = self._hass.data[SOMFY_DOMAIN]["state"]
        elements = self._hass.data[SOMFY_DOMAIN]["elements"]
        _LOGGER.debug("Device : %s - Device type : %s", self._device, self._deviceType)
        _LOGGER.debug("Name : %s - Friendly name: %s", self._name, self._fname)
        if self._device == "general" :
            if state:
                if SENSOR_STATE[self._deviceType][state[self._deviceType]]:
                    self._state = SENSOR_STATE[self._deviceType][state[self._deviceType]]
                else:
                    self._state = SENSOR_STATE[self._deviceType][state[self._deviceType]["other_state"]]
                    _LOGGER.debug("Not matched")
                _LOGGER.debug("State : %s", self._state)
            else:
                _LOGGER.debug("State is empty")
        else:
            if elements:
                _LOGGER.debug(elements)
                self._fname = elements[self._device]["elt_name"]
                self._state_attr.update(elements[self._device])
                self._state_attr.update({"friendly_name2": self._fname})
                _LOGGER.debug("item_type: %s", elements[self._device]["item_type"])
                self._name = self._fname
                if (elements[self._device]["item_type"] == "typedm") and (self._deviceType == "elt_maison"):
                    self._device_class = "motion"
                if SENSOR_STATE[self._deviceType][elements[self._device][self._deviceType]]:
                    self._state = SENSOR_STATE[self._deviceType][elements[self._device][self._deviceType]]
                    _LOGGER.debug("%s : %s", self._deviceType, elements[self._device][self._deviceType])
                else:
                    self._state = SENSOR_STATE[self._device_class][elements[self._device]["other_state"]]
                    _LOGGER.debug("Not matched")
                _LOGGER.debug("State : %s", self._state)
            else:
                _LOGGER.debug("State is empty")
        _LOGGER.debug("########## END OF UPDATE  ################")
