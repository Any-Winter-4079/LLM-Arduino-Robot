#include <Servo.h>

// Servo pin definitions
const int UP_DOWN_SERVO_PIN = 9;
const int LEFT_RIGHT_SERVO_PIN = A0;

// Servo angle constants
const int DOWN_ANGLE = 50;
const int UP_ANGLE = 110;
const int VERT_CENTER_ANGLE = 80;
const int LEFT_ANGLE = 120;
const int RIGHT_ANGLE = 60;
const int HORIZ_CENTER_ANGLE = 90;

// Timing constants
const int DELAY_TIME = 400;  // 0.4 seconds
const int NUM_ITERATIONS = 3;

// Servo objects
Servo up_down_servo;
Servo left_right_servo;

// Movement direction enums
enum VerticalDirection { UP, DOWN, VERT_CENTER };
enum HorizontalDirection { LEFT, RIGHT, HORIZ_CENTER };

void setup() {
    initializeServos();
    runTestSequence();
}

void loop() {
    // Test sequence runs once in setup(), so loop() is empty
}

void initializeServos() {
    up_down_servo.attach(UP_DOWN_SERVO_PIN);
    left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);
    centerServos();
}

void centerServos() {
    moveServos(VERT_CENTER, HORIZ_CENTER);
}

void moveServos(VerticalDirection vertDir, HorizontalDirection horizDir) {
    int vertAngle = getVerticalAngle(vertDir);
    int horizAngle = getHorizontalAngle(horizDir);
    
    up_down_servo.write(vertAngle);
    left_right_servo.write(horizAngle);
    delay(DELAY_TIME);
}

int getVerticalAngle(VerticalDirection dir) {
    switch(dir) {
        case UP: return UP_ANGLE;
        case DOWN: return DOWN_ANGLE;
        case VERT_CENTER: return VERT_CENTER_ANGLE;
        default: return VERT_CENTER_ANGLE;
    }
}

int getHorizontalAngle(HorizontalDirection dir) {
    switch(dir) {
        case LEFT: return LEFT_ANGLE;
        case RIGHT: return RIGHT_ANGLE;
        case HORIZ_CENTER: return HORIZ_CENTER_ANGLE;
        default: return HORIZ_CENTER_ANGLE;
    }
}

void runTestSequence() {
    moveLeftRight();
    moveUpDown();
    moveDiagonalTopLeftBottomRight();
    moveDiagonalTopRightBottomLeft();
}

void moveLeftRight() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveServos(VERT_CENTER, LEFT);
        moveServos(VERT_CENTER, RIGHT);
    }
    centerServos();
}

void moveUpDown() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveServos(UP, HORIZ_CENTER);
        moveServos(DOWN, HORIZ_CENTER);
    }
    centerServos();
}

void moveDiagonalTopLeftBottomRight() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveServos(UP, LEFT);
        moveServos(DOWN, RIGHT);
    }
    centerServos();
}

void moveDiagonalTopRightBottomLeft() {
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        moveServos(UP, RIGHT);
        moveServos(DOWN, LEFT);
    }
    centerServos();
}