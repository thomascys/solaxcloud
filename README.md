# SolaxCloud integration for Home Assistant.

## Installation
- Place this solaxcloud directory under the custom_components directory.
- Add the sensor to your configuration.yaml:
    ```
    sensor:
    - platform: solaxcloud
      username: USERNAME
      password: PASSWORD
      site_id: SITE ID
    ```
- To obtain your site id. Login to solaxcloud.com and click on Sites in the left menu. Inspect the Site-name with your browser developer tools. You should see something like "showAnalysis('xxxxxxxxxxxxxx','Home')" in the html code.
- Verify that the custom entities are available in home assistant.
