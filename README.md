# 🧳 SAS Award Finder (Home Assistant Integration)

This custom integration fetches **award seat availability from SAS** (Scandinavian Airlines) and displays it as a sensor in Home Assistant.

You can add multiple sensors (e.g. OSL→LYR, OSL→EWR, etc.) — each fetching availability for the selected month.

---

## ✈️ Features
- Realtime award availability lookup from SAS API  
- Multiple destinations per sensor  
- Displays both **outbound** and **inbound** seats  
- Configurable from the UI (no YAML)  
- Optional alerts when seats become available  

---

## 🧩 Installation (via HACS)

1. Go to **HACS → Integrations → Custom repositories**
2. Add your repository URL  
   Example:  
https://github.com/<yourusername/home-assistant-sas-award-finder

Type: `Integration`
3. Click **Add**
4. Then install **SAS Award Finder**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → + Add Integration → SAS Award Finder**

---

## ⚙️ Configuration
When adding the integration, specify:
- **Origin** airport (e.g., `OSL`)
- **Destinations** (comma separated, e.g., `EWR,JFK`)
- **Month** (e.g., `2026-08`)
- **Direct**: True/False
- **Market** (default: `no-no`)

---

## 🧱 Example Dashboard

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

📦 Credits

Developed by AndersH and ChatGPT
Data provided by SAS API (unofficial)

