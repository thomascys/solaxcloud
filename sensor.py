import json
import requests
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from datetime import date

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SITE_ID = "site_id"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_SITE_ID): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    solax_cloud = SolaxCloud(hass, config[CONF_USERNAME], config[CONF_PASSWORD], config[CONF_SITE_ID])
    add_entities([SolarPowerSensor(hass, solax_cloud),
                  GridPowerSensor(hass, solax_cloud),
                  InverterTemperatureSensor(hass, solax_cloud),
                  InverterTotalYieldSensor(hass, solax_cloud),
                  InverterDailyYieldSensor(hass, solax_cloud)
                 ], True)

class SolaxCloud:
    def __init__(self, hass, username, password, site_id):
        self.hass = hass
        self.logger = logging.getLogger(__name__)
        self._username = username
        self._password = password
        self._site_id = site_id
        self._base_url = 'http://www.solaxcloud.com:6080'
        self._login_endpoint = '/proxy/login/login'
        self._data_endpoint = '/proxy/mysite/getInverterInfo'
        self.data = []
        self.inverter_name = 'Solax'

    def get_token_id(self):
        resp = None
        try:
            uri = self._base_url + self._login_endpoint + '?userName=' + self._username + '&password=' + self._password
            resp = requests.post(uri)
            json_obj = resp.json()

            # {'exception': '用户名或密码输入错误!', 'result': None, 'success': False}
            if json_obj['success'] == False:
                if json_obj['exception'] == '用户名或密码输入错误!':
                    self.logger.error('Invalid Username or Password')
                elif json_obj['exception'] != '用户名或密码输入错误!':
                    self.logger.error('Other error:\r\n%s', json_obj['exception'])

                return json_obj
            else:
                return json_obj['result']['tokenId']
        except requests.exceptions.ConnectionError:
            self.logger.error('Connection Error:\r\n%s', resp)
            raise ConnectionAbortedError


    # http://www.solaxcloud.com:6080/proxy/mysite/getInverterInfo?siteId=<SiteId>&tokenId=<TokenId>
    def get_data(self):
        resp = None
        try:
            token_id = self.get_token_id()
            uri = self._base_url + self._data_endpoint + '?siteId=' + self._site_id + '&tokenId=' + token_id
            resp = requests.post(uri)
            json_obj = resp.json()
            self.data = json_obj['result'].pop()
            self.inverter_name = self.data['inverterSN']
        except requests.exceptions.ConnectionError:
            return resp

class InverterTotalYieldSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Total yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['totalYield'])

    @property
    def unit_of_measurement(self):
        return 'kW'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

class InverterDailyYieldSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Daily yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['todayYield'])

    @property
    def unit_of_measurement(self):
        return 'kW'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

class InverterTemperatureSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = solax_cloud.inverter_name + ' Temperature'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['temperature'])

    @property
    def unit_of_measurement(self):
        return 'C'

    @property
    def icon(self):
        return 'mdi:thermometer'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

class SolarPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._state = None
        self.hass = hass
        self._name = solax_cloud.inverter_name + ' PV power'
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['powerdc1'] + data['powerdc2'])

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

class GridPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._state = None
        self.hass = hass
        self._name = solax_cloud.inverter_name +' Grid power'
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(self.solax_cloud.data['gridPower'])

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:solar-power'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.solax_cloud.get_data()

# Other setup with info on enumerating the type fields
# https://github.com/wills106/homeassistant-config/blob/master/packages/solax.yaml

# Response example:
# {
#     "exception": "查询成功!",
#     "result": [
#         {
#             "wifiSN": "SWSMMS9LCT",
#             "deviceName": null,
#             "inverterSN": "XBE502F0000000",
#             "accessTime": 1588579594000,
#             "lastUpdateTime": 1588683933442,
#             "pv1Current": 0.0,
#             "pv2Current": 0.0,
#             "pv3Current": null,
#             "pv4Current": null,
#             "pv1Voltage": 81.8,
#             "pv2Voltage": 79.1,
#             "pv3Voltage": null,
#             "pv4Voltage": null,
#             "powerdc1": 0.0,
#             "powerdc2": 0.0,
#             "powerdc3": null,
#             "powerdc4": null,
#             "totalYield": 30.0,
#             "todayYield": 27.7,
#             "iac1": 0.2,
#             "vac1": 228.7,
#             "pac1": 0.0,
#             "fac1": 49.97,
#             "iac2": 0.0,
#             "vac2": 0.0,
#             "pac2": 0.0,
#             "fac2": 0.0,
#             "iac3": 0.0,
#             "vac3": 0.0,
#             "pac3": 0.0,
#             "fac3": 0.0,
#             "gridPower": 0.0,
#             "feedinPower": 0.0,
#             "temperature": 34.0,
#             "hours": 28,
#             "accessTimes": "2020-05-04 16:06:34",
#             "lastUpdateTimes": "2020-05-05 21:05:33",
#             "phaseFlag": 1,
#             "batteryFlag": 0,
#             "inverterType": "4",
#             "enableFlag": "1",
#             "workMode": 0,
#             "pvCount": 2,
#             "transportType": 2
#         }
#     ],
#     "success": true
# }