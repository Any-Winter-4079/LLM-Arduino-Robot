/*
* L298N Motor Driver Test Sketch
* Tests basic movement functions of a two-motor robot using L298N driver
* Features:
* - Forward/backward movement
* - Left/right turning
* - Variable speed control
* - Basic test sequence
*/

// Motor pin definitions for L298N motor driver
const int RIGHT_MOTOR_SPEED = 6;  // ENA on L298N - Enable pin for right motor
const int RIGHT_MOTOR_DIR1 = 8;   // IN1 on L298N - Direction control 1 for right motor  
const int RIGHT_MOTOR_DIR2 = 7;   // IN2 on L298N - Direction control 2 for right motor
const int LEFT_MOTOR_SPEED = 3;   // ENB on L298N - Enable pin for left motor
const int LEFT_MOTOR_DIR1 = 5;    // IN3 on L298N - Direction control 1 for left motor
const int LEFT_MOTOR_DIR2 = 4;    // IN4 on L298N - Direction control 2 for left motor

// Speed constants for PWM control
const int TOP_SPEED = 255;        // Maximum speed (100% duty cycle)
const int LOW_SPEED = 135;        // ~53% speed
const int NO_SPEED = 0;           // Stopped (0% duty cycle)

// Delay time constants (in milliseconds)
const int SHORT_DELAY = 500;      // Brief pause between actions
const int MEDIUM_DELAY = 2000;    // Standard pause between actions  
const int LONG_DELAY = 3000;      // Extended pause between actions

// Direction enums for more readable code
enum Direction {
   FORWARD,                      // Forward movement
   BACKWARD                      // Backward movement
};

enum Turn {
   LEFT,                         // Left turn
   RIGHT                         // Right turn
};

/*
* Initial setup function - runs once
* Initializes motor pins and executes test sequence
*/
void setup() {
   initializeMotors();

   // Execute test sequence of movements
   advance(FORWARD, LOW_SPEED, MEDIUM_DELAY);      // Move forward
   advance(BACKWARD, LOW_SPEED, MEDIUM_DELAY);     // Move backward
   turn(LEFT, TOP_SPEED, LONG_DELAY);              // Turn left
   stop(MEDIUM_DELAY);                             // Pause
   turn(RIGHT, TOP_SPEED, LONG_DELAY);             // Turn right
   stop(MEDIUM_DELAY);                             // Final pause
}

/*
* Main program loop
* Empty since this is a one-time test sequence
*/
void loop() {
   // The test sequence runs once in setup(), so loop() is empty
}

/*
* Configures all motor control pins as outputs
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
* Sets direction for a single motor using H-bridge control pins
* Parameters:
* motor1, motor2: The two direction control pins for the motor
* direction: FORWARD or BACKWARD enum value
*/
void setMotorDirection(int motor1, int motor2, Direction direction) {
   digitalWrite(motor1, direction == FORWARD ? HIGH : LOW);
   digitalWrite(motor2, direction == FORWARD ? LOW : HIGH);
}

/*
* Sets motor speed using PWM
* Parameters:
* motorSpeedPin: Enable pin for the motor
* speed: PWM value (0-255)
*/
void setMotorSpeed(int motorSpeedPin, int speed) {
   analogWrite(motorSpeedPin, constrain(speed, 0, 255));
}

/*
* Moves robot forward or backward
* Parameters:
* direction: FORWARD or BACKWARD
* speed: Motor speed (0-255)
* duration: How long to move in milliseconds
*/
void advance(Direction direction, int speed, int duration) {
   setMotorDirection(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, direction);
   setMotorDirection(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, direction);
   setMotorSpeed(RIGHT_MOTOR_SPEED, speed);
   setMotorSpeed(LEFT_MOTOR_SPEED, speed);
   delay(duration);
}

/*
* Turns robot left or right by running motors in opposite directions
* Parameters:
* turnDirection: LEFT or RIGHT
* speed: Motor speed (0-255)
* duration: How long to turn in milliseconds
*/
void turn(Turn turnDirection, int speed, int duration) {
   // Determine individual motor directions based on turn direction
   Direction rightMotorDir = (turnDirection == LEFT) ? FORWARD : BACKWARD;
   Direction leftMotorDir = (turnDirection == LEFT) ? BACKWARD : FORWARD;
   
   setMotorDirection(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, rightMotorDir);
   setMotorDirection(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, leftMotorDir);
   setMotorSpeed(RIGHT_MOTOR_SPEED, speed);
   setMotorSpeed(LEFT_MOTOR_SPEED, speed);
   delay(duration);
}

/*
* Stops both motors
* Parameters:
* duration: How long to remain stopped in milliseconds
*/
void stop(int duration) {
   setMotorSpeed(RIGHT_MOTOR_SPEED, NO_SPEED);
   setMotorSpeed(LEFT_MOTOR_SPEED, NO_SPEED);
   delay(duration);
}