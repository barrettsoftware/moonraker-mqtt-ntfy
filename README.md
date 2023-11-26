# moonraker-mqtt-ntfy
Python script to sent NTFY notifications based on MQTT information from moonraker.

# Set the following Variables:
The script is written to track the status of two printers. It can easily be extended. For each printer you must map the MQTT topic for the state and filename.

MQTT_BROKER = "192.168.1.20"
MQTT_PORT = 1883 
MQTT_USERNAME = ""  # Optional
MQTT_PASSWORD = ""  # Optional
MQTT_TOPICS = [
    "printer-1/klipper/state/print_stats/state",
    "printer-2/klipper/state/print_stats/state",
    "printer-1/klipper/state/print_stats/filename",
    "printer-2/klipper/state/print_stats/filename"
]

# ntfy Settings
NTFY_URL = "https://ntfy.domain.com/topic"
