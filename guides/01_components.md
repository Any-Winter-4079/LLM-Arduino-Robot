For the construction of the Arduino robot prototype, the following electronic devices are used:

- 1x 7.4V rechargeable battery -in this case, an ELEGOO micro-USB rechargeable battery- for motors, motor controller, Arduino, servos, ESP32-WROVER, sound detector, microphone, amplifier, speaker, and OLED display.
- 4x 1.2V rechargeable AA batteries (with series battery holder and switch) -to provide 4.8V to the ESP32-CAMs, one for each robot eye.
- 2x Adjustable buck converters with potentiometer -to reduce to 5V and 3.3V, for various components that don't accept 7.4V directly.
- 1x 2-pin switch -to easily turn the robot on and off, noting that another switch would be needed if one wasn't available in the battery holder (since ESP32-CAMs have separate power supply to avoid voltage spikes during motor and servo use).
- 1x 400-pin breadboard -for creating 2 power lines, at 7.4V (directly from battery) and 5V (from a voltage reducer).
- 2x 170-pin breadboards -one for sound input (KY-037, INMP441), in the front of the robot, and another for output (MAX98357A), in its rear.
- Male-to-male, male-to-female, and female-to-female Dupont cables for robot wiring.
- 1x Arduino Uno Rev3 -to send commands received from ESP32-WROVER to the motor controller (for wheel movement) and/or servos (for eye movement).
- 1x DC barrel jack (DC power jack) -to power the Arduino with 7.4V, internally regulated by Arduino to 5V.
- 1x L298N motor controller -to receive direction commands from Arduino (forward rotation, backward rotation, or stop) and intensity (rotation speed) to send to motors.
- 2x SG-90 servos -to move the eyes horizontally and vertically -according to angles received from Arduino Uno.
- 2x ESP32-CAM -in this case, Ai-Thinker and M5Stack Wide, although both could have been the same model- to establish a web server responsible for sending frames on demand to the computer (where the robot's brain runs).
- 1x ESP32-WROVER (or ESP32-CAM without camera use) -in this case, 1x Freenove ESP32-WROVER CAM Board- to manage movement command reception (to send to Arduino Uno) and audio sending (to computer) and reception (from computer).
- 2x OV2640 -one per ESP32-CAM- with 160-degree fisheye lens, to allow eye movement (with embedded camera) using a 75mm cable (longer than the original 21mm cable).
- 1x 128x64 SSD1306 I2C OLED display -to show information such as WiFi network from which IP address is acquired, useful in case of multiple possibilities, or robot's internal state ('Listening…', 'Thinking…').
- 1x KY-037 sound detection microphone -to start sending audio to computer when a certain sound threshold is exceeded.
- 1x INMP441 I2S microphone -to capture said sound, and be sent by ESP32-WROVER to computer to determine, using Speech-to-Text, if it's noise or a natural language phrase, and in that case, send it to the language model.
- 1x MAX98357A I2S amplifier -to receive audio sent to ESP32-WROVER from computer, referring to language model response converted to audio using Text-to-Speech and forwarded by this to the amplifier.
- 1x 3W 8Ω speaker -for playing audio received by the amplifier.
- 2x 3-6V DC motors with gearbox -in this case, with Dupont termination- to attach to each of the front wheels to direct robot movement.

Additionally, the following materials are used for chassis construction, component mounting, and eye manufacturing:

- 2x Wheels -1x for each gearbox motor.
- 2x Metal motor mounts -to screw each motor to chassis with 2 horizontal and 2 vertical screws.
- 1x ~3cm Ø caster wheel -to place in the central rear of robot.
- 1x ~40x40x0.3cm wood or particleboard -for chassis.
- 1x ~11x4x0.8cm wooden board -for support pieces in vertical and horizontal eye movement.
- ~4cm length M3 hexagonal spacers -to separate different chassis levels.
- ~1.5cm length M3 screws -both headed and double-threaded (i.e., headless).
- M3 washers.
- Regular and self-locking M3 nuts.
- 2x M2 screws - to attach SSD1306 I2C OLED display to chassis.
- 2x M2 nuts - to secure display to chassis.
- 4x Ping pong balls -to serve as mold for pouring resin to manufacture eyes.
- 1x Epoxy Resin Kit.
- Paints and brushes -for painting resin.
- Red thread -for veins on eyes.
- Blue Tack -for non-permanent fixings.
- Colored adhesive tape -to label cables by type (e.g., power, motors, servos, audio, etc.).
- Super Glue-3 to join SG-90's servo horn (pressure-fitted to it) to vertical rotation cylinder -noting that with this design the servo is replaceable, being pressure-detachable from horn.

Similarly, although not part of the robot, the following tools and accessories are used for its manufacture and/or testing:

- 1x Digital multimeter -for voltage verification.
- 1x Steel saw -24 TPI- for chassis.
- Sandpaper -for chassis.
- 1x Drill Kit -with M3 size.
- 1x Soldering Kit -for soldering pins to INMP441 and MAX98357A.
- Pliers and wire strippers.
- Screwdrivers.
- 1x C-clamp -for holding during cutting.
- 1x Measuring tape.
- 1x Scissors.
- 1x Printer and paper- to print eye iris and ESP32-CAM calibration pattern.

And finally, for robot operation, the following is required:

- 1x Computer -with adequate specifications for LLM.
- 1x Router for internet access and/or phone with hotspot, to connect 2x ESP32-CAM, ESP32-WROVER and computer to the same network, as well as for internet access (necessary depending on functions callable by LLM, such as internet search).
- 1x USB-A to Serial converter (for uploading code to some ESP32-CAM models, like Ai-Thinker) or USB-A to USB-C Cable (for other models, like M5Stack Wide).
- 1x USB A to USB B cable -for flashing code to Arduino Uno.
- 1x USB A to micro-USB cable -for recharging 7.4V battery.
- 1x AA battery charger.
