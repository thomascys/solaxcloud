# SolaxCloud integration for Home Assistant.

## Installation
- Change the credentials in sensor.py ('your-username', 'your-password', 'your-inverter-serial', 'your-inverter-ssid').
- Place this solaxcloud directory under custom_components directory.
- Edit your configuration.yaml and add the following under sensor: `- platform: solaxcloud`
- Verify that the custom entities are available.

## Todo
- Make the credentials configurable instead of hard-coded.