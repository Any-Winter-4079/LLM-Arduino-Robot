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

## Camera Setup

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
