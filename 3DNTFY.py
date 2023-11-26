import paho.mqtt.client as mqtt
import requests
import json

# MQTT Settings
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

# Track the last status and filename for each printer
last_status = {}
last_filename = {}

# Mapping of MQTT topic names to friendly printer names
friendly_names = {
    "printer-1": "Friendlyname1",
    "printer-2": "Friendlyname2"
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
    
    # Extract printer name key from topic
    topic_parts = msg.topic.split('/')
    if topic_parts[0] == 'printer':
        printer_name_key = '/'.join(topic_parts[:2])  # Joins 'printer' and the next part (e.g., 'ender-basement')
    else:
        printer_name_key = topic_parts[0]  # Directly takes the first part for topics like 'printer-sovol'
    printer_name = friendly_names.get(printer_name_key, printer_name_key)

    if "filename" in msg.topic:
        # This message is about the filename
        last_filename[printer_name] = payload
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

    # Format the message with filename
    message = f"{emoji} {printer_name} {friendly_status.get(status, 'status changed to ' + status)}. Printing: {filename}"

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
