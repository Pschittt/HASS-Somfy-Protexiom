import configparser
from .somfy import Somfy
import logging
from collections import defaultdict

import voluptuous as vol

#from homeassistant.helpers.discovery import load_platform
from homeassistant.const import CONF_URL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity

# from const import *
from .const import DOMAIN, SENSOR_TYPES, SOMFY_COMPONENTS, SOMFY_DEVICES_TYPE, CONF_CODES, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_CODES): vol.All(
                    {'key_A1': cv.string, 'key_A2': cv.string, 'key_A3': cv.string, 'key_A4': cv.string, 'key_A5': cv.string,
                    'key_B1': cv.string, 'key_B2': cv.string, 'key_B3': cv.string, 'key_B4': cv.string, 'key_B5': cv.string,
                    'key_C1': cv.string, 'key_C2': cv.string, 'key_C3': cv.string, 'key_C4': cv.string, 'key_C5': cv.string,
                    'key_D1': cv.string, 'key_D2': cv.string, 'key_D3': cv.string, 'key_D4': cv.string, 'key_D5': cv.string,
                    'key_E1': cv.string, 'key_E2': cv.string, 'key_E3': cv.string, 'key_E4': cv.string, 'key_E5': cv.string,
                    'key_F1': cv.string, 'key_F2': cv.string, 'key_F3': cv.string, 'key_F4': cv.string, 'key_F5': cv.string,
                    }
                ),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    _LOGGER.debug("************ Starting SOMFY *************") 
    url = config[DOMAIN][CONF_URL]
    password = config[DOMAIN][CONF_PASSWORD]
    codes = config[DOMAIN][CONF_CODES]
    _LOGGER.debug("codes :")
    _LOGGER.debug(codes)
    
    try: 
        somfy = Somfy(url, password, codes)
        somfy.login()
        elements = somfy.get_elements()
        somfy.logout()
    except:
        _LOGGER.exception("Error when trying to log in")
        return False
    
    hass.data[DOMAIN] = {"controller": somfy, "devices": {"general":[]}, "state": "", "elements": "", "activation_alarm_code": password}
    
    ## Add the general states as devices
    for device in SOMFY_DEVICES_TYPE:
        _LOGGER.debug(device)
        hass.data[DOMAIN]["devices"]["general"].append(device)

    ## Add all elements as devices
    for deviceId, deviceTypes in elements.items():
        hass.data[DOMAIN]["devices"].update({deviceId : []})
        for typeId, typeValue in deviceTypes.items():
            if (typeId in SENSOR_TYPES) and (typeValue != "itemhidden"):
                hass.data[DOMAIN]["devices"][deviceId].append(typeId)

    
    for component in SOMFY_COMPONENTS:
        _LOGGER.debug("Components : ")
        _LOGGER.debug(component)
        discovery.load_platform(hass, component, DOMAIN, {}, config)
        
    return True
