# 🧳 SAS Award Finder (Home Assistant Integration)

**SAS Award Finder** is a Home Assistant custom integration that fetches award seat availability from SAS (Scandinavian Airlines)
and exposes it as sensors. Each sensor represents a combination of origin, destinations and month and provides detailed JSON attributes
with outbound and inbound availability arrays suitable for dashboarding (table cards) and automations.

**Author:** AndersH

## Features
- Query SAS award availability for a given month and destinations
- Support multiple destinations (comma-separated) per sensor (e.g. `EWR,JFK`)
- Configurable from the UI (Config Flow)
- Provides `outbound` and `inbound` arrays as attributes for easy table display
- Polls the SAS API every hour (configurable in code)

## Installation (HACS)
1. In HACS, go to **Integrations → Custom repositories**.
2. Add repository URL: `https://github.com/<yourusername>/home-assistant-sas-award-finder`
   - Type: **Integration**
3. Install **SAS Award Finder** from HACS.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → + Add Integration → SAS Award Finder** and fill in the form.

## YAML (if you prefer)
This integration supports UI config via config flow. If you prefer YAML, you can still create sensor entries by using the platform.
(Not required once the integration supports config flow.)

## Example Lovelace Table Card (flex-table-card)
```yaml
type: custom:flex-table-card
title: SAS OSL–LYR Award Availability
entities:
  include: sensor.sas_award_finder_osl_lyr
columns:
  - name: Date
    data: date
  - name: Total
    data: availableSeatsTotal
  - name: AG
    data: AG
  - name: AP
    data: AP
data_path: outbound
```

## Full-featured Automation Example (Alert when availability appears)
This example sends a notification with the list of dates that have available seats for outbound flights.
Replace `notify.mobile_app_yourphone` with your notify target.
```yaml
alias: "SAS Award Availability Alert - Full"
trigger:
  - platform: time_pattern
    hours: "/6"  # every 6 hours
condition: []
action:
  - variables:
      sensor_entity: sensor.sas_award_finder_osl_lyr
      outbound: "{ state_attr(sensor_entity, 'outbound') | default([]) }"
      available_dates: >
        { (outbound | selectattr('availableSeatsTotal', '>', 0) | map(attribute='date') | list) | join(', ') }
  - choose:
      - conditions:
          - condition: template
            value_template: "{ available_dates != '' }"
        sequence:
          - service: notify.mobile_app_yourphone
            data:
              title: "✈️ SAS Award Seats Available (OSL → LYR)"
              message: "Available dates: { available_dates }"
  - default: []
```

## License
MIT License — see LICENSE file.

## Notes
This integration uses an unofficial SAS API endpoint discovered from the public site. Use responsibly and be mindful of API rate limits.
