# Anker SOLIX V1 Smart EV Charger for Home Assistant

Custom integration for the Anker SOLIX V1 Smart EV Charger using Modbus TCP.

## Features
- **Monitoring**: Voltage (L1-L3), Current (L1-L3), Total Power, Session Energy, Session Duration, and Charging Status.
- **Control**: 
  - Start/Stop charging.
  - Set Max Current Limit (6A - 32A).
  - Set Phase Mode (Auto, Single-Phase, Three-Phase).

## Installation
1. Copy the `custom_components/anker_smart_ev` directory to your Home Assistant `config/custom_components/` folder.
2. Restart Home Assistant.
3. In the HA UI, go to **Settings** > **Devices & Services** > **Add Integration**.
4. Search for "Anker SOLIX V1 Smart EV Charger".

## Configuration
Before adding the integration, ensure **Modbus TCP** is enabled in the Anker SOLIX app:
1. Open the Anker app, select your V1 Smart EV Charger.
2. Tap the **Settings** icon.
3. Select **Integrations**.
4. Toggle **Modbus TCP** to **On**.
5. Use the IP address displayed in the app for the Home Assistant configuration.

## Support
This integration uses the Modbus TCP protocol (V1.0.0). It is not affiliated with Anker Innovations Ltd.
