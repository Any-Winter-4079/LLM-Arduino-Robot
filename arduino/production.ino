/*
 * Robot Control System
 * This program controls a robot with servo-driven eyes and DC motors for movement.
 * Features:
 * - Dual servo control for eye movement (up/down and left/right)
 * - Dual DC motor control for robot movement
 * - OLED display for status messages
 * - Serial communication for receiving commands
 */

// Library includes for servo control, I2C communication, and OLED display
#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Fonts/FreeMono9pt7b.h>

// Servo pin definitions
const int UP_DOWN_SERVO_PIN = 9;       // Controls vertical eye movement
const int LEFT_RIGHT_SERVO_PIN = A0;   // Controls horizontal eye movement

// Servo angle limits and center positions
const int DOWN_ANGLE = 50;             // Lowest vertical position
const int UP_ANGLE = 110;              // Highest vertical position
const int VERT_CENTER_ANGLE = 80;      // Vertical center position
const int LEFT_ANGLE = 120;            // Leftmost position
const int RIGHT_ANGLE = 60;            // Rightmost position
const int HORIZ_CENTER_ANGLE = 90;     // Horizontal center position

// L298N Motor Driver pin configurations
const int RIGHT_MOTOR_SPEED = 6;       // Enable pin for right motor (ENA)
const int RIGHT_MOTOR_DIR1 = 8;        // Direction control 1 for right motor (IN1)
const int RIGHT_MOTOR_DIR2 = 7;        // Direction control 2 for right motor (IN2)
const int LEFT_MOTOR_SPEED = 3;        // Enable pin for left motor (ENB)
const int LEFT_MOTOR_DIR1 = 5;         // Direction control 1 for left motor (IN3)
const int LEFT_MOTOR_DIR2 = 4;         // Direction control 2 for left motor (IN4)

// Timing constants (in milliseconds)
const int SHORT_DELAY = 500;           // Brief pause between actions
const int MEDIUM_DELAY = 1000;         // Standard pause between actions
const int LONG_DELAY = 3000;           // Extended pause between actions

// OLED display configuration
const int SCREEN_WIDTH = 128;          // Display width in pixels
const int SCREEN_HEIGHT = 64;          // Display height in pixels
const int OLED_RESET = -1;             // Reset pin (shared with Arduino reset)

// Movement pattern configuration
const int NUM_ITERATIONS = 3;          // Number of times to repeat movement patterns
const int DELAY_TIME = 400;            // Delay between movement steps

// Object instantiation
Servo up_down_servo;                   // Servo object for vertical movement
Servo left_right_servo;                // Servo object for horizontal movement
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);  // OLED display object

// Function declarations with descriptions
void updateDisplay(const String& message);           // Updates OLED display with given message
void moveLeftRightServo(int angle);                  // Controls horizontal eye movement
void moveUpDownServo(int angle);                     // Controls vertical eye movement
void stopMotors();                                   // Stops both DC motors
void moveMotors(String leftDirection, String rightDirection, int speed);  // Controls motor movement

/*
 * Initial setup function - runs once at startup
 * Initializes serial communication, servos, display, and motors
 * Performs initial movement sequence
 */
void setup() {
    Serial.begin(9600);                // Initialize serial communication
    initializeServos();                // Setup servo motors
    initializeDisplay();               // Setup OLED display
    initializeMotors();                // Setup DC motors
    performInitialMotions();           // Execute startup movement sequence
}

/*
 * Main program loop
 * Continuously checks for and processes serial commands
 */
void loop() {
    if (Serial.available()) {
        String received_data = Serial.readStringUntil('\n');
        processReceivedData(received_data);
    }
}

/*
 * Initializes servo motors by attaching them to their respective pins
 */
void initializeServos() {
    up_down_servo.attach(UP_DOWN_SERVO_PIN);
    left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);
}

/*
 * Initializes OLED display and shows initial ready message
 */
void initializeDisplay() {
    // Initialize display with I2C address 0x3C
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
        for(;;);  // Don't proceed if display initialization fails
    }
    display.display();
    delay(LONG_DELAY);
    
    // Configure display settings
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,6);
    display.cp437(true);

    updateDisplay("Ready");
    delay(DELAY_TIME);
}

/*
 * Configures motor control pins as outputs
 */
void initializeMotors() {
    pinMode(RIGHT_MOTOR_SPEED, OUTPUT);
    pinMode(RIGHT_MOTOR_DIR1, OUTPUT);
    pinMode(RIGHT_MOTOR_DIR2, OUTPUT);
    pinMode(LEFT_MOTOR_SPEED, OUTPUT);
    pinMode(LEFT_MOTOR_DIR1, OUTPUT);
    pinMode(LEFT_MOTOR_DIR2, OUTPUT);
}

/*
 * Executes initial movement sequence to demonstrate functionality
 */
void performInitialMotions() {
    // Center the eyes initially
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    moveUpDownServo(UP_ANGLE);
    delay(DELAY_TIME);

    // Perform demonstration movements
    performHorizontalMovement();
    performVerticalMovement();
    performDiagonalMovement();

    // Return to default position
    moveUpDownServo(UP_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
}

/*
 * Executes horizontal eye movement pattern
 */
void performHorizontalMovement() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        // Look left
        moveUpDownServo(VERT_CENTER_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        updateServoDisplay(LEFT_ANGLE, VERT_CENTER_ANGLE);
        delay(DELAY_TIME);

        // Look right
        moveUpDownServo(VERT_CENTER_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        updateServoDisplay(RIGHT_ANGLE, VERT_CENTER_ANGLE);
        delay(DELAY_TIME);
    }
    // Return to center
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    updateServoDisplay(HORIZ_CENTER_ANGLE, VERT_CENTER_ANGLE);
    delay(DELAY_TIME);
}

/*
 * Executes vertical eye movement pattern
 */
void performVerticalMovement() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        // Look up
        moveLeftRightServo(HORIZ_CENTER_ANGLE);
        moveUpDownServo(UP_ANGLE);
        updateServoDisplay(HORIZ_CENTER_ANGLE, UP_ANGLE);
        delay(DELAY_TIME);

        // Look down
        moveLeftRightServo(HORIZ_CENTER_ANGLE);
        moveUpDownServo(DOWN_ANGLE);
        updateServoDisplay(HORIZ_CENTER_ANGLE, DOWN_ANGLE);
        delay(DELAY_TIME);
    }
    // Return to center
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    updateServoDisplay(HORIZ_CENTER_ANGLE, VERT_CENTER_ANGLE);
    delay(DELAY_TIME);
}

/*
 * Executes diagonal eye movement patterns
 */
void performDiagonalMovement() {
    // First diagonal pattern (upper-left to lower-right)
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveUpDownServo(UP_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        updateServoDisplay(LEFT_ANGLE, UP_ANGLE);
        delay(DELAY_TIME);

        moveUpDownServo(DOWN_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        updateServoDisplay(RIGHT_ANGLE, DOWN_ANGLE);
        delay(DELAY_TIME);
    }
    // Return to center
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    updateServoDisplay(HORIZ_CENTER_ANGLE, VERT_CENTER_ANGLE);
    delay(DELAY_TIME);

    // Second diagonal pattern (upper-right to lower-left)
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveUpDownServo(UP_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        updateServoDisplay(RIGHT_ANGLE, UP_ANGLE);
        delay(DELAY_TIME);

        moveUpDownServo(DOWN_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        updateServoDisplay(LEFT_ANGLE, DOWN_ANGLE);
        delay(DELAY_TIME);
    }
}

/*
 * Updates OLED display with given message
 */
void updateDisplay(const String& message) {
    display.clearDisplay();
    display.setFont(&FreeMono9pt7b);
    display.setCursor(0,15);
    display.print(message);
    display.display();
}

/*
 * Controls horizontal servo movement with angle constraints
 */
void moveLeftRightServo(int angle) {
    angle = constrain(angle, RIGHT_ANGLE, LEFT_ANGLE);
    left_right_servo.write(angle);
}

/*
 * Controls vertical servo movement with angle constraints
 */
void moveUpDownServo(int angle) {
    angle = constrain(angle, DOWN_ANGLE, UP_ANGLE);
    up_down_servo.write(angle);
}

/*
 * Stops both DC motors
 */
void stopMotors() {
    digitalWrite(RIGHT_MOTOR_DIR1, LOW);
    digitalWrite(RIGHT_MOTOR_DIR2, LOW);
    digitalWrite(LEFT_MOTOR_DIR1, LOW);
    digitalWrite(LEFT_MOTOR_DIR2, LOW);
    analogWrite(RIGHT_MOTOR_SPEED, 0);
    analogWrite(LEFT_MOTOR_SPEED, 0);
}

/*
 * Controls DC motor movement
 * Parameters:
 * leftDirection: "10" for forward, "01" for reverse, "00" for stop
 * rightDirection: same as leftDirection
 * speed: motor speed (0-255)
 */
void moveMotors(String leftDirection, String rightDirection, int speed) {
    // Configure left motor direction
    if (leftDirection == "10") {
        digitalWrite(LEFT_MOTOR_DIR1, HIGH);
        digitalWrite(LEFT_MOTOR_DIR2, LOW);
    } else if (leftDirection == "01") {
        digitalWrite(LEFT_MOTOR_DIR1, LOW);
        digitalWrite(LEFT_MOTOR_DIR2, HIGH);
    } else {
        digitalWrite(LEFT_MOTOR_DIR1, LOW);
        digitalWrite(LEFT_MOTOR_DIR2, LOW);
    }

    // Configure right motor direction
    if (rightDirection == "10") {
        digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
        digitalWrite(RIGHT_MOTOR_DIR2, LOW);
    } else if (rightDirection == "01") {
        digitalWrite(RIGHT_MOTOR_DIR1, LOW);
        digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
    } else {
        digitalWrite(RIGHT_MOTOR_DIR1, LOW);
        digitalWrite(RIGHT_MOTOR_DIR2, LOW);
    }

    // Set motor speeds
    analogWrite(LEFT_MOTOR_SPEED, speed);
    analogWrite(RIGHT_MOTOR_SPEED, speed);

    delay(SHORT_DELAY);
    stopMotors();
}

/*
 * Updates OLED display with current servo positions
 */
void updateServoDisplay(int leftRightAngle, int upDownAngle) {
    display.clearDisplay();
    display.setFont(&FreeMono9pt7b);
    display.setCursor(0,15);
    display.print("LR:" + String(leftRightAngle));
    display.setCursor(0,30);
    display.print("UD:" + String(upDownAngle));
    display.display();
}

/*
 * Processes serial commands received from ESP32-WROVER
 * Supports commands for:
 * - SSID display
 * - Motor control
 * - Servo positioning
 * - Status messages
 */
void processReceivedData(const String& received_data) {
    if (received_data.startsWith("SSID:")) {
        String ssid = received_data.substring(5);
        updateDisplay(ssid);
    }
    else if (received_data.startsWith("leftMD:") || 
            received_data.startsWith("rightMD:") || 
            received_data.startsWith("motorsS:") || 
            received_data.startsWith("angleVP:") || 
            received_data.startsWith("angleHP:"))
    {
        processMotorAndServoCommands(received_data);
    }
    else if (received_data.startsWith("Listening") || received_data.startsWith("Thinking")) {
        updateDisplay(received_data);
    }
}

/*
 * Parses and executes motor and servo movement commands
 * Command format: "parameter:value,parameter:value,..."
 * Parameters:
 * - leftMD: left motor direction
 * - rightMD: right motor direction
 * - motorsS: motor speed
 * - angleVP: vertical position
 * - angleHP: horizontal position
 */
void processMotorAndServoCommands(const String& received_data) {
    String leftMD_str = "", rightMD_str = "";
    int motorsS = -1, angleVP = -1, angleHP = -1;

    // Parse comma-separated commands
    int start = 0;
    while (start < received_data.length()) {
        int end = received_data.indexOf(',', start);
        if (end == -1) end = received_data.length();
        
        String part = received_data.substring(start, end);
        
        // Extract command parameters
        if (part.startsWith("leftMD:")) {
            leftMD_str = part.substring(7);
        } else if (part.startsWith("rightMD:")) {
            rightMD_str = part.substring(8);
        } else if (part.startsWith("motorsS:")) {
            motorsS = part.substring(8).toInt();
        } else if (part.startsWith("angleVP:")) {
            angleVP = part.substring(8).toInt();
        } else if (part.startsWith("angleHP:")) {
            angleHP = part.substring(8).toInt();
        }

        start = end + 1;
    }

    // Execute motor commands if present
    if (leftMD_str != "" && rightMD_str != "") {
        moveMotors(leftMD_str, rightMD_str, motorsS != -1 ? motorsS : 0);
    }

    // Execute servo commands if present
    if (angleVP != -1) moveUpDownServo(angleVP);
    if (angleHP != -1) moveLeftRightServo(angleHP);
    if (angleVP != -1 || angleHP != -1) {
        updateServoDisplay(
            angleHP != -1 ? angleHP : left_right_servo.read(),
            angleVP != -1 ? angleVP : up_down_servo.read()
        );
    }
}