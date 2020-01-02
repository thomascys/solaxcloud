import asyncio
import aiohttp
import async_timeout
import json
import requests

from datetime import timedelta
from datetime import date
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

def setup_platform(hass, config, add_devices, discovery_info=None):
    solax_cloud = SolaxCloud(hass, 'your-username', 'your-password', 'your-inverter-serial', 'your-inverter-ssid')
    add_devices([SolarPowerSensor(hass, solax_cloud), GridPowerSensor(hass, solax_cloud), InverterTemperatureSensor(hass, solax_cloud), InverterTotalYieldSensor(hass, solax_cloud), InverterDailyYieldSensor(hass, solax_cloud)], True)

class SolaxCloud:
    def __init__(self, hass, username, password, inverter_serial, inverter_ssid):
        self.hass = hass
        self._username = username
        self._password = password
        self._inverter_serial = inverter_serial
        self._inverter_ssid = inverter_ssid
        self._base_url = 'http://47.254.152.24:6080'
        self._login_endpoint = '/proxy/login/login'
        self._data_endpoint = '/proxy/inverter/getDailyInfo'
        self.data = []

    def get_token_id(self):
        resp = None
        try:
            uri = self._base_url + self._login_endpoint + '?userName=' + self._username + '&password=' + self._password
            resp = requests.post(uri)
            json_obj = resp.json()
            return json_obj['result']['tokenId']
        except requests.exceptions.ConnectionError:
            return resp

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def get_data(self):
        resp = None
        try:
            today = date.today()
            current_date = today.strftime('%Y-%m-%d')
            token_id = self.get_token_id()
            uri = self._base_url + self._data_endpoint + '?inverterSn=' + self._inverter_serial + '&wifiSn=' + self._inverter_ssid + '&tokenId=' + token_id + '&today=' + current_date
            resp = requests.post(uri)
            json_obj = resp.json()
            self.data = json_obj['result'].pop()
        except requests.exceptions.ConnectionError:
            return resp

class InverterTotalYieldSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = 'Total yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['yieldtotal'])

    @property
    def unit_of_measurement(self):
        return 'kW'

    @property
    def icon(self):
        return 'mdi:gauge-full'

    def update(self):
        self.solax_cloud.get_data()

class InverterDailyYieldSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = 'Daily yield'
        self.hass = hass
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(data['yieldtoday'])

    @property
    def unit_of_measurement(self):
        return 'kW'

    @property
    def icon(self):
        return 'mdi:gauge-low'

    def update(self):
        self.solax_cloud.get_data()

class InverterTemperatureSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._name = 'Temperature'
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

    def update(self):
        self.solax_cloud.get_data()

class SolarPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._state = None
        self.hass = hass
        self._name = 'Solar power'
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
        return 'mdi:gauge'

    def update(self):
        self.solax_cloud.get_data()

class GridPowerSensor(Entity):
    def __init__(self, hass, solax_cloud):
        self._state = None
        self.hass = hass
        self._name = 'Grid power'
        self.solax_cloud = solax_cloud

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.solax_cloud.data
        return int(self.solax_cloud.data['gridpower'])

    @property
    def unit_of_measurement(self):
        return 'W'

    @property
    def icon(self):
        return 'mdi:gauge'

    def update(self):
        self.solax_cloud.get_data()
