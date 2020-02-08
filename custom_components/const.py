from homeassistant.components.binary_sensor import *
from homeassistant.const import (
    STATE_OFF, 
    STATE_ON,
)

DOMAIN = 'protexiom'
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2)
SCAN_INTERVAL = timedelta(minutes=2)

CONF_CODES = "codes"

SOMFY_COMPONENTS = ["sensor","binary_sensor", "alarm_control_panel"]
SOMFY_DEVICES_TYPE = ["battery", "communication", "door", "alarm", "material", "zone_a", "zone_b", "zone_c"]

SENSOR_TYPES = {
    "battery": ["battery", "", None, DEVICE_CLASS_BATTERY],
    "communication": ["communication", "", "mdi:access-point", DEVICE_CLASS_CONNECTIVITY],
    "door": ["door", "", "", DEVICE_CLASS_DOOR],
    "alarm": ["alarm", "", "", DEVICE_CLASS_SAFETY],
    "material": ["material", "", None, DEVICE_CLASS_PLUG],
    "zone_a": ["zone_a", "", "", DEVICE_CLASS_LOCK],
    "zone_b": ["zone_b", "", "", DEVICE_CLASS_LOCK],
    "zone_c": ["zone_c", "", "", DEVICE_CLASS_LOCK],
    "motion":["motion", "", None, DEVICE_CLASS_MOTION],
    "item_pause": ["material", "", None, DEVICE_CLASS_PLUG],
    "elt_pile": ["battery", "", None, DEVICE_CLASS_BATTERY],
    "elt_maison":["alarm", "", None, DEVICE_CLASS_MOTION],
    "elt_onde": ["communication", "", "mdi:access-point", DEVICE_CLASS_CONNECTIVITY],
    "elt_porte": ["door", "", "", DEVICE_CLASS_DOOR]
}

SENSOR_STATE = {
    "battery": {"Piles OK": STATE_OFF,"Piles faibles": STATE_ON},
    "communication": {"other_state": STATE_OFF,"Communication radio OK": STATE_ON},
    "door": {"Porte ou fenêtre fermée": STATE_OFF,"Porte ou fenêtre ouverte": STATE_ON},
    "alarm": {"Pas d'alarme": STATE_OFF,"Alarme Intrusion": STATE_ON, "itemhouseok": STATE_OFF},
    "material": {"other_state": STATE_OFF,"Boîtier OK": STATE_ON},
    "zone_a": {"OFF": STATE_ON,"ON": STATE_OFF},
    "zone_b": {"OFF": STATE_ON,"ON": STATE_OFF},
    "zone_c": {"OFF": STATE_ON,"ON": STATE_OFF},
    "motion":{"itemhouseok": STATE_OFF, "itemhouseintrusion": STATE_ON},
    "item_pause": {"running": STATE_ON, "other_state": STATE_OFF},
    "elt_pile": {"itembattok": STATE_OFF, "itembattnok": STATE_ON},
    "elt_maison": {"itemhouseok": STATE_OFF, "itemhouseintrusion": STATE_ON},
    "elt_onde": {"itemcomok": STATE_ON, "itemcomnok": STATE_OFF},
    "elt_porte": {"itemdoorok": STATE_OFF, "itemdoornok": STATE_ON}
}
