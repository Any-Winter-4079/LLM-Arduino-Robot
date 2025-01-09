# Notes on the `servos/` code:

## Computer Setup

- Define in this line whether the robot and computer will share the phone hotspot (True) or the home WiFi (False) as the common network for communication (e.g., sending and receiving of commands):

```
USE_HOTSPOT = True
```

- Define in this line the WROVER's IPs (requested within `esp32/wrover/production.ino`) the phone hotspot or home WiFi will assign:

```
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"
```

## ESP32 Setup

- Make sure `esp32/wrover/production.ino` has been uploaded to the WROVER to receive the servo commands on the `/command` endpoint (e.g., `http://172.20.10.12/command`) and forward them to the Arduino.

## Arduino Setup

- Make sure `arduino/production.ino` has been uploaded to the Arduino (to send the servo commands to the SG-90s).

## Comments

- Note if you power the WROVER (e.g., via USB-C) from the computer, you can see the WROVER logs in real time.
