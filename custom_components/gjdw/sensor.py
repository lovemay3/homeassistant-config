
import logging
import time, datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta 
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, ATTR_ATTRIBUTION, CONF_ID
    )
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from .gjdw import GJDWData

_Log=logging.getLogger(__name__)

DEFAULT_NAME = 'gjdw'
OPENID = 'openid'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(OPENID): cv.string,
    vol.Optional(CONF_NAME, default= DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    sensor_name = config.get(CONF_NAME)
    openid = config.get(OPENID)
    add_devices([GJDW(hass,sensor_name,openid)])

class GJDW(Entity):
    """Representation of a guojiadianwang """
    def __init__(self,hass,sensor_name,openid):
        self._hass = hass
        self.attributes = {}
        self._state = None
        self._name = sensor_name
        self._openid = openid
        self._data = GJDWData(openid)
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """   mdi   ."""
        return 'mdi:flash'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attributes

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return "元"

    def getData(self):
        self._data.getData()
        self._state = self._data.info.remain
        info = self._data.info
        params = {
            'last_date':info.last_date,
            'latest_month':info.latest_month,
            'latest_electricity':info.latest_electricity,
            'latest_total':info.latest_total,
            'current_year_total':info.current_year_total,
            'current_year_electricity':info.current_year_electricity
        }

        self.attributes = {
            '当前余额' : self.state + self.unit_of_measurement,
            '余额最后一次记录时间': info.last_date,
            info.latest_month+'月' : '电费:'+str(info.latest_total)+self.unit_of_measurement+' 电量:'+str(info.latest_electricity)+'度',
            '总电费': str(info.current_year_total)+self.unit_of_measurement,
            '总电量': str(info.current_year_electricity)+'度',
            'params':params
        }

    def update(self):
        self._hass.async_add_executor_job(self.getData)

        

