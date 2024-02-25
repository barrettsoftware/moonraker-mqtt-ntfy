import paho.mqtt.client as mqtt
import requests
import json

# MQTT Settings
MQTT_BROKER = "192.168.1.6"
MQTT_PORT = 1883 
MQTT_USERNAME = ""  # Optional
MQTT_PASSWORD = ""  # Optional
MQTT_TOPICS = [
    "printer-A/klipper/state/print_stats/state",
    "printer-A/klipper/state/print_stats/filename",
    "printer-A/klipper/state/print_stats/total_duration",  # Added duration topic for printer-A
    "printer-B/klipper/state/print_stats/state",
    "printer-B/klipper/state/print_stats/filename",
    "printer-b/klipper/state/print_stats/total_duration"    # Added duration topic for printer-B
]

# ntfy Settings
NTFY_URL = "https://ntfy.domain.com/topic"

# Track the last status, filename, and print duration for each printer
last_status = {}
last_filename = {}
last_print_duration = {}  # Track the last print duration

# Mapping of MQTT topic names to friendly printer names
friendly_names = {
    "printer-A": "Prusa",
    "printer-B": "Ender"
}

# Emoji mapping for different statuses
status_emojis = {
    "printing": "🖨️",  # Printer emoji
    "complete": "✅",   # Check mark emoji
    "cancelled": "❌"   # Cross mark emoji
}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in MQTT_TOPICS:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} {str(msg.payload)}")
    payload = json.loads(msg.payload.decode())["value"]

    topic_parts = msg.topic.split('/')
    printer_name_key = '/'.join(topic_parts[:2])  # Joins 'printer' and the next part
    printer_name = friendly_names.get(printer_name_key, printer_name_key)

    if "filename" in msg.topic:
        last_filename[printer_name] = payload
    elif "print_duration" in msg.topic:
        # Convert print duration from seconds to hours and minutes
        duration_hours, duration_minutes = divmod(int(payload), 3600), divmod(int(payload) % 3600, 60)
        last_print_duration[printer_name] = f"{duration_hours[0]}h {duration_minutes[0]}m"
    else:
        # This message is about the printer status
        if last_status.get(printer_name) != payload:
            last_status[printer_name] = payload
            send_notification(printer_name, payload)

def send_notification(printer_name, status):
    friendly_status = {
        "printing": "has started printing",
        "complete": "has finished printing",
        "cancelled": "print was cancelled"
    }
    emoji = status_emojis.get(status, "")
    filename = last_filename.get(printer_name, "unknown file")
    duration = last_print_duration.get(printer_name, "duration unknown")  # Get the print duration

    # Format the message with filename and duration
    message = f"{emoji} {printer_name} {friendly_status.get(status, 'status changed to ' + status)}. Printing: {filename}. Duration: {duration}"

    headers = {
        "Content-Type": "text/plain; charset=utf-8"
    }

    try:
        response = requests.post(NTFY_URL, headers=headers, data=message.encode('utf-8'))
        print(f"Attempting to send notification: {message}")
        print(f"Notification response: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  # Set the username and password for MQTT
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
