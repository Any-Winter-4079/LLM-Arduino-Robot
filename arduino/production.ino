#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Fonts/FreeMono9pt7b.h>

// Constants for servo pins
const int UP_DOWN_SERVO_PIN = 9;
const int LEFT_RIGHT_SERVO_PIN = A0;

// Constants for servo angles
const int DOWN_ANGLE = 50;
const int UP_ANGLE = 110;
const int VERT_CENTER_ANGLE = 80;
const int LEFT_ANGLE = 120;
const int RIGHT_ANGLE = 60;
const int HORIZ_CENTER_ANGLE = 90;

// Constants for motor pins
const int RIGHT_MOTOR_SPEED = 6;  // ENA
const int RIGHT_MOTOR_DIR1 = 8;   // IN1
const int RIGHT_MOTOR_DIR2 = 7;   // IN2
const int LEFT_MOTOR_SPEED = 3;   // ENB
const int LEFT_MOTOR_DIR1 = 5;    // IN3
const int LEFT_MOTOR_DIR2 = 4;    // IN4

// Constants for delays
const int SHORT_DELAY = 500;   // 0.5 seconds
const int MEDIUM_DELAY = 1000; // 1 second
const int LONG_DELAY = 3000;   // 3 seconds

// Constants for display
const int SCREEN_WIDTH = 128;
const int SCREEN_HEIGHT = 64;
const int OLED_RESET = -1;

// Other constants
const int NUM_ITERATIONS = 3;
const int DELAY_TIME = 400;

// Servo objects
Servo up_down_servo;
Servo left_right_servo;

// Display object
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Function prototypes
void updateDisplay(const String& message);
void moveLeftRightServo(int angle);
void moveUpDownServo(int angle);
void stopRightMotor();
void stopLeftMotor();
void moveRightMotor(String direction, int speed);
void moveLeftMotor(String direction, int speed);

void setup() {
    Serial.begin(9600);
    initializeServos();
    initializeDisplay();
    performInitialMotions();
}

void loop() {
    if (Serial.available()) {
        String received_data = Serial.readStringUntil('\n');
        processReceivedData(received_data);
    }
}

void initializeServos() {
    up_down_servo.attach(UP_DOWN_SERVO_PIN);
    left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);
}

void initializeDisplay() {
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
        for(;;);
    }
    display.display();
    delay(LONG_DELAY);
    
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,6);
    display.cp437(true);

    updateDisplay("Ready");
    delay(DELAY_TIME);
}

void performInitialMotions() {
    // Center the eyes
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    moveUpDownServo(UP_ANGLE);
    delay(DELAY_TIME);

    // Perform horizontal, vertical, and diagonal movements
    performHorizontalMovement();
    performVerticalMovement();
    performDiagonalMovement();

    // Move to initial positions
    moveUpDownServo(UP_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
}

void performHorizontalMovement() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveUpDownServo(VERT_CENTER_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        delay(DELAY_TIME);

        moveUpDownServo(VERT_CENTER_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        delay(DELAY_TIME);
    }
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);
}

void performVerticalMovement() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveLeftRightServo(HORIZ_CENTER_ANGLE);
        moveUpDownServo(UP_ANGLE);
        delay(DELAY_TIME);

        moveLeftRightServo(HORIZ_CENTER_ANGLE);
        moveUpDownServo(DOWN_ANGLE);
        delay(DELAY_TIME);
    }
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);
}

void performDiagonalMovement() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveUpDownServo(UP_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        delay(DELAY_TIME);

        moveUpDownServo(DOWN_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        delay(DELAY_TIME);
    }
    moveUpDownServo(VERT_CENTER_ANGLE);
    moveLeftRightServo(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);

    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveUpDownServo(UP_ANGLE);
        moveLeftRightServo(RIGHT_ANGLE);
        delay(DELAY_TIME);

        moveUpDownServo(DOWN_ANGLE);
        moveLeftRightServo(LEFT_ANGLE);
        delay(DELAY_TIME);
    }
}

void updateDisplay(const String& message) {
    display.clearDisplay();
    display.setFont(&FreeMono9pt7b);
    display.setCursor(0,15);
    display.print(message);
    display.display();
}

void moveLeftRightServo(int angle) {
    angle = constrain(angle, RIGHT_ANGLE, LEFT_ANGLE);
    left_right_servo.write(angle);
    updateDisplay("AngleLR:" + String(angle));
}

void moveUpDownServo(int angle) {
    angle = constrain(angle, DOWN_ANGLE, UP_ANGLE);
    up_down_servo.write(angle);
    updateDisplay("AngleUD:" + String(angle));
}

void stopRightMotor() {
    digitalWrite(RIGHT_MOTOR_DIR1, LOW);
    digitalWrite(RIGHT_MOTOR_DIR2, LOW);
}

void stopLeftMotor() {
    digitalWrite(LEFT_MOTOR_DIR1, LOW);
    digitalWrite(LEFT_MOTOR_DIR2, LOW);
}

void moveRightMotor(String direction, int speed) {
    if (direction == "10") {
        digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
        digitalWrite(RIGHT_MOTOR_DIR2, LOW);
    } else if (direction == "01") {
        digitalWrite(RIGHT_MOTOR_DIR1, LOW);
        digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
    } else {
        digitalWrite(RIGHT_MOTOR_DIR1, LOW);
        digitalWrite(RIGHT_MOTOR_DIR2, LOW);
    }
    analogWrite(RIGHT_MOTOR_SPEED, speed);
    delay(SHORT_DELAY);
    stopRightMotor();
}

void moveLeftMotor(String direction, int speed) {
    if (direction == "10") {
        digitalWrite(LEFT_MOTOR_DIR1, HIGH);
        digitalWrite(LEFT_MOTOR_DIR2, LOW);
    } else if (direction == "01") {
        digitalWrite(LEFT_MOTOR_DIR1, LOW);
        digitalWrite(LEFT_MOTOR_DIR2, HIGH);
    } else {
        digitalWrite(LEFT_MOTOR_DIR1, LOW);
        digitalWrite(LEFT_MOTOR_DIR2, LOW);
    }
    analogWrite(LEFT_MOTOR_SPEED, speed);
    delay(SHORT_DELAY);
    stopLeftMotor();
}

void processReceivedData(const String& received_data) {
    if (received_data.startsWith("SSID:")) {
        String ssid = received_data.substring(5);
        updateDisplay(ssid);
    }
    // leftMD: left motor direction
    // rightMD: right motor direction
    // motorsS: motors speed -shared
    // angleVP: angle for vertical eyes position
    // angleHP: angle for horizontal eyes position
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

void processMotorAndServoCommands(const String& received_data) {
    String leftMD_str = "", rightMD_str = "";
    int motorsS = -1, angleVP = -1, angleHP = -1;

    int start = 0;
    while (start < received_data.length()) {
        int end = received_data.indexOf(',', start);
        if (end == -1) end = received_data.length();
        
        String part = received_data.substring(start, end);
        
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

    if (leftMD_str != "") moveLeftMotor(leftMD_str, motorsS != -1 ? motorsS : 0);
    if (rightMD_str != "") moveRightMotor(rightMD_str, motorsS != -1 ? motorsS : 0);
    if (angleVP != -1) moveUpDownServo(angleVP);
    if (angleHP != -1) moveLeftRightServo(angleHP);
}