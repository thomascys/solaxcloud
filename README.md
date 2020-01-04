# SolaxCloud integration for Home Assistant.

## Installation
- Change the credentials in sensor.py ('your-username', 'your-password', 'your-inverter-serial', 'your-inverter-ssid').
- Place this solaxcloud directory under custom_components directory.
- Edit your configuration.yaml:
    ```
    sensor:
    - platform: seventeentrack
        username: USERNAME
        password: PASSWORD
        inverter_serial: SERIAL
        inverter_number: NUMBER
    ```
- Verify that the custom entities are available.
