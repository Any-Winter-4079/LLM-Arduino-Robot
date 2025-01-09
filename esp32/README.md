# Notes on the `esp32/` code:

The ESP32 components handle image capturing, audio processing, and communication between the computer and Arduino:

## Directory Structure

- `cam/` contains the production code for the ESP32-CAMs:
  - `aithinker-production.ino`
  - `m5stackwide-production.ino`
  - Both cameras send images to the computer for (LLM-brain) processing
- `wrover/production.ino`
  - Receives movement commands from LLM-brain on computer and forwards them to Arduino
  - Sends (captured) human speech to LLM-brain on computer and receives returning (LLM) speech

## ESP32 Setup

- Define in these lines your home WiFi' and phone hotspot's SSID and password:

```
const char* ssid1 = "";                     // Home WiFi's SSID
const char* password1 = "";                 // Home WiFi's password
```

```
const char* ssid2 = "";                     // Phone hotspot's SSID
const char* password2 = "";                 // Phone hotspot's password
```

- Code upload requires either USB-C port or USB-to-serial adapter with:
  - FTDI 5V → ESP32-CAM 5V (FTDI set to 3.3V)
  - FTDI GND → ESP32-CAM GND
  - FTDI TXD → ESP32-CAM U0R
  - FTDI RXD → ESP32-CAM U0T
  - ESP32-CAM GND → ESP32-CAM IO0 (for flash mode)
- IO0 must be grounded during upload, then disconnected to run

## Network Configuration

- Dual network support (home WiFi + phone hotspot fallback)
- For phone hotspot setup:
  1. Enable hotspot
  2. Enable "Maximize Compatibility"
  3. Power on robot
  4. Connect computer to hotspot

## Dependencies

Required libraries (to place in `Arduino/libraries/`):

- https://github.com/espressif/esp32-camera
- https://github.com/me-no-dev/AsyncTCP
- https://github.com/me-no-dev/ESPAsyncWebServer

For example in:

```
Users/you/Documents/Arduino/libraries/esp32-camera-master
Users/you/Documents/Arduino/libraries/AsyncTCP
Users/you/Documents/Arduino/libraries/ESPAsyncWebServer-master
```

## Credits

The AsyncBufferResponse, AsyncFrameResponse and sendJpg() code that (together with ESPAsyncWebServer) enabled **stable** (i.e., not out-of-order) images up to 37 fps is from:
https://gist.github.com/me-no-dev/d34fba51a8f059ac559bf62002e61aa3
