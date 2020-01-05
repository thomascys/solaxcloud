# SolaxCloud integration for Home Assistant.

## Installation
- Place this solaxcloud directory under the custom_components directory.
- Add the sensor to your configuration.yaml:
    ```
    sensor:
    - platform: solaxcloud
      username: USERNAME
      password: PASSWORD
      inverter_serial: SERIAL
      inverter_number: NUMBER
    ```
- Verify that the custom entities are available in home assistant
