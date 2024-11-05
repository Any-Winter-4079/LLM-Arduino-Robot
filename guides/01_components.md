For the construction of the Arduino robot prototype, the following electronic devices are used:

- 1x 7.4V rechargeable battery - in this case, an ELEGOO micro-USB rechargeable battery - for powering motors, motor controller, Arduino, servos, ESP32-WROVER, sound detector, microphone, amplifier, speaker, and OLED display
- 4x 1.2V rechargeable AA batteries - with a series battery holder and switch - to provide 4.8V to the ESP32-CAMs, one for each robot eye
- 2x adjustable buck converters - with potentiometer adjustment - to reduce voltage to 5V and 3.3V for components that don't accept 7.4V directly
- 1x 2-pin switch - to control the robot's main power (noting that a second switch would be needed if the battery holder lacks one, since the ESP32-CAMs use separate power to avoid voltage spikes during motor and servo operation)
- 1x 400-pin breadboard - to create two power distribution lines: 7.4V (direct from the battery) and 5V (from the buck converter)
- 2x 170-pin breadboards - one for sound input components (the KY-037 and INMP441) at the front, and one for sound output components (the MAX98357A) at the rear
- Male-to-male, male-to-female, and female-to-female Dupont cables - for all wiring connections
- 1x Arduino Uno Rev3 - to send the commands received from the ESP32-WROVER to the motor controller (for wheel movement) and to the servos (for eye movement)
- 1x DC barrel jack - to supply 7.4V to the Arduino, which internally regulates it to 5V
- 1x L298N motor controller - to receive both direction commands (forward rotation, backward rotation, or stop) and intensity commands (rotation speed) from the Arduino to control the motors
- 2x SG-90 servos - to move the eyes horizontally and vertically based on angle commands from the Arduino
- 2x ESP32-CAM - using Ai-Thinker and M5Stack Wide models (though both could be the same model) - to run web servers that send camera frames to the computer running the robot's brain
- 1x ESP32-WROVER - using a Freenove ESP32-WROVER CAM Board - to handle movement command reception (to send to the Arduino) and two-way audio communication with the computer
- 2x OV2640 cameras - one per ESP32-CAM - with 160-degree fisheye lenses and 75mm cables (longer than the original 21mm cables) to enable eye movement with embedded cameras
- 1x 128x64 SSD1306 I2C OLED display - to show system information such as the connected WiFi network and the robot's internal state ('Listening...', 'Thinking...')
- 1x KY-037 sound detection microphone - to trigger audio transmission to the computer when sound exceeds a threshold
- 1x INMP441 I2S microphone - to capture audio for the ESP32-WROVER to send to the computer, where Speech-to-Text determines if it's noise or speech to be processed by the language model
- 1x MAX98357A I2S amplifier - to process the audio sent to the ESP32-WROVER from the computer (containing the language model's response converted by Text-to-Speech)
- 1x 3W 8Ω speaker - to play the processed audio from the amplifier
- 2x 3-6V DC motors with gearboxes - with Dupont termination - to drive the front wheels for robot movement

For chassis construction, component mounting, and eye fabrication:

- 2x wheels - one for each gearbox motor
- 2x metal motor mounts - to secure each motor to the chassis using four screws (two horizontal, two vertical)
- 1x caster wheel (approximately 3cm diameter) - for the robot's central rear support
- 1x wooden board or particleboard (approximately 40x40x0.3cm) - for the main chassis
- 1x wooden board (approximately 11x4x0.8cm) - for eye movement support structures
- M3 hexagonal spacers (approximately 4cm length) - to separate chassis levels
- M3 screws (approximately 1.5cm length) - both headed and headless (double-threaded)
- M3 washers
- M3 nuts - both standard and self-locking types
- 2x M2 screws - to mount the OLED display
- 2x M2 nuts - to secure the OLED display
- 4x ping pong balls - to serve as molds for the resin eyes
- 1x epoxy resin kit
- Paints and brushes - for eye coloring
- Red thread - for eye vein details
- Blue Tack - for temporary component mounting
- Colored adhesive tape - for cable identification by function (power, motors, servos, audio, etc.)
- Super Glue-3 - to attach the SG-90's servo horn (pressure-fitted) to the vertical rotation cylinder, allowing servo replacement

Tools and accessories for construction and testing:

- 1x digital multimeter - for voltage testing
- 1x steel saw (24 TPI) - for chassis cutting
- Sandpaper - for chassis finishing
- 1x drill kit - with M3 bits
- 1x soldering kit - for the INMP441 and MAX98357A pin connections
- Pliers and wire strippers
- Screwdrivers
- 1x C-clamp - for secure cutting
- 1x measuring tape
- 1x scissors
- 1x printer and paper - for eye iris patterns and ESP32-CAM calibration charts

Required for operation:

- 1x computer - with specifications suitable for running the LLM
- 1x router or phone hotspot - to network the ESP32-CAMs, ESP32-WROVER, and computer, and provide - internet access for LLM functions
- 1x USB-A to Serial converter - for Ai-Thinker ESP32-CAM programming, or USB-A to USB-C cable for M5Stack Wide
- 1x USB-A to USB-B cable - for Arduino Uno programming
- 1x USB-A to micro-USB cable - for the 7.4V battery charging
- 1x AA battery charger
