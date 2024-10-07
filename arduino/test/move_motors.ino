// Motor pin definitions for L298N motor driver
const int RIGHT_MOTOR_SPEED = 6;  // ENA on L298N
const int RIGHT_MOTOR_DIR1 = 8;   // IN1 on L298N
const int RIGHT_MOTOR_DIR2 = 7;   // IN2 on L298N
const int LEFT_MOTOR_SPEED = 3;   // ENB on L298N
const int LEFT_MOTOR_DIR1 = 5;    // IN3 on L298N
const int LEFT_MOTOR_DIR2 = 4;    // IN4 on L298N

// Speed constants
const int TOP_SPEED = 255;        // 100% duty cycle
const int LOW_SPEED = 135;
const int NO_SPEED = 0;           // 0% duty cycle

// Delay times
const int SHORT_DELAY = 500;   // 0.5 seconds
const int MEDIUM_DELAY = 2000; // 2 seconds
const int LONG_DELAY = 3000;   // 3 seconds

// Direction enums
enum Direction {
    FORWARD,
    BACKWARD
};

enum Turn {
    LEFT,
    RIGHT
};

void setup() {
    initializeMotors();

    // Test sequence
    advance(FORWARD, LOW_SPEED, MEDIUM_DELAY);
    advance(BACKWARD, LOW_SPEED, MEDIUM_DELAY);
    turn(LEFT, TOP_SPEED, LONG_DELAY);
    stop(MEDIUM_DELAY);
    turn(RIGHT, TOP_SPEED, LONG_DELAY);
    stop(MEDIUM_DELAY);
}

void loop() {
    // The test sequence runs once in setup(), so loop() is empty
}

void initializeMotors() {
    pinMode(RIGHT_MOTOR_SPEED, OUTPUT);
    pinMode(RIGHT_MOTOR_DIR1, OUTPUT);
    pinMode(RIGHT_MOTOR_DIR2, OUTPUT);
    pinMode(LEFT_MOTOR_SPEED, OUTPUT);
    pinMode(LEFT_MOTOR_DIR1, OUTPUT);
    pinMode(LEFT_MOTOR_DIR2, OUTPUT);
}

void setMotorDirection(int motor1, int motor2, Direction direction) {
    digitalWrite(motor1, direction == FORWARD ? HIGH : LOW);
    digitalWrite(motor2, direction == FORWARD ? LOW : HIGH);
}

void setMotorSpeed(int motorSpeedPin, int speed) {
    analogWrite(motorSpeedPin, constrain(speed, 0, 255));
}

void advance(Direction direction, int speed, int duration) {
    setMotorDirection(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, direction);
    setMotorDirection(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, direction);
    setMotorSpeed(RIGHT_MOTOR_SPEED, speed);
    setMotorSpeed(LEFT_MOTOR_SPEED, speed);
    delay(duration);
}

void turn(Turn turnDirection, int speed, int duration) {
    Direction rightMotorDir = (turnDirection == LEFT) ? FORWARD : BACKWARD;
    Direction leftMotorDir = (turnDirection == LEFT) ? BACKWARD : FORWARD;
    
    setMotorDirection(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, rightMotorDir);
    setMotorDirection(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, leftMotorDir);
    setMotorSpeed(RIGHT_MOTOR_SPEED, speed);
    setMotorSpeed(LEFT_MOTOR_SPEED, speed);
    delay(duration);
}

void stop(int duration) {
    setMotorSpeed(RIGHT_MOTOR_SPEED, NO_SPEED);
    setMotorSpeed(LEFT_MOTOR_SPEED, NO_SPEED);
    delay(duration);
}