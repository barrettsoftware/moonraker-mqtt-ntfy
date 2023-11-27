## Purpose of the Script
This Python script will send NTFY notifications based on MQTT information from moonraker. The script can run on any host that has access to the moonraker instance and the ntfy server. You can even run this on the computer running moonraker/klipper. This script allows you to monitor 3D printers running moonraker with the NTFY service. The script is written to track the status of two printers. It can easily be extended. For each printer you must map the MQTT topic for the *state* and *filename*.

## Step 1: Add MQTT snippet to moonraker.conf
```
[mqtt]
address: 192.168.1.20
port: 1883
mqtt_protocol: v3.1.1
enable_moonraker_api: False
instance_name: printer-sovol
publish_split_status: True
status_objects:
    webhooks
    heater_bed
    extruder
    print_stats
    toolhead
    display_status
default_qos: 0
```

# Step 2: Set the following Variables in the Script:
```
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
```
# ntfy Settings
```
NTFY_URL = "https://ntfy.domain.com/topic"
```

# Step 3: Run the Script
You can just run the script manually with 
```
python3 3DNTFY.py
```
What I did is created a service so that the script is always running. This requires you to create new service helper file and then
 turn the script into a service. I put the script itself into /etc/scripts/3DNTFY.py and then ran the following commands to turn it into a service.


```
touch /etc/systemd/system/3dprinter_notify.service
sudo nano /etc/systemd/system/3dprinter_notify.service
```
Paste the following snippet into the .service file. Make sure to edit the password.
```
[Unit]
Description=3D Printer Notification Service
After=network.target

[Service]
Type=simple
User=your_username
ExecStart=/usr/bin/python3 /etc/scripts/3DNTFY.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Press *CTRL+X* to save and close.

Then enter the following commands to create, start, and then check the service.

```
sudo systemctl daemon-reload
sudo systemctl enable 3dprinter_notify.service
sudo systemctl start 3dprinter_notify.service
sudo systemctl status 3dprinter_notify.service
```
Your final output should show that the service is running. 