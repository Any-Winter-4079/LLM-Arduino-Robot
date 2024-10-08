# Notes on the `motors/` code:

- Define in this line whether the robot and computer will share the phone's hotspot (True) or the primary network's WiFi (False) as a common network for communication (e.g. sending and receiving of commands):

```
USE_HOTSPOT = True
```

- Define in this line the ESP32-WROVER's IPs (requested within `esp32/wrover/production.ino`) assigned by the phone's hotspot and primary network's (e.g. home's) WiFi:

```
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"
```

- Make sure `esp32/wrover/production.ino` has been uploaded to the ESP32-WROVER -to receive the motor commands on the `/command` endpoint (e.g. `http://172.20.10.12/command`) to forward them to the Arduino.

- Make sure `arduino/production.ino` has been uploaded to the Arduino (to send the motor commands to the L298N).

- Note if you power the ESP32-WROVER (e.g. with a USB-C) from the computer, you can see the ESP32-WROVER logs in real time.
