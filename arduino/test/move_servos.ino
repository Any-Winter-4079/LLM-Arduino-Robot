/*
* Dual Servo Control Test
* Controls two servos to create coordinated eye-like movements
* Features:
* - Vertical (up/down) and horizontal (left/right) servo control
* - Center positioning
* - Test sequence with various movement patterns
* - Diagonal movement capabilities
*/

#include <Servo.h>

// Servo pin definitions
const int UP_DOWN_SERVO_PIN = 9;       // Pin for vertical movement servo
const int LEFT_RIGHT_SERVO_PIN = A0;   // Pin for horizontal movement servo

// Servo angle limits and center positions
const int DOWN_ANGLE = 50;             // Lowest vertical position (degrees)
const int UP_ANGLE = 110;              // Highest vertical position (degrees)
const int VERT_CENTER_ANGLE = 80;      // Vertical center position (degrees)
const int LEFT_ANGLE = 120;            // Leftmost position (degrees)
const int RIGHT_ANGLE = 60;            // Rightmost position (degrees)
const int HORIZ_CENTER_ANGLE = 90;     // Horizontal center position (degrees)

// Timing and iteration constants
const int DELAY_TIME = 400;            // Delay between movements (milliseconds)
const int NUM_ITERATIONS = 3;          // Number of times to repeat each pattern

// Servo objects
Servo up_down_servo;                   // Servo for vertical movement
Servo left_right_servo;                // Servo for horizontal movement

// Enums for movement directions
enum VerticalDirection { 
   UP,                                // Move to highest position
   DOWN,                              // Move to lowest position
   VERT_CENTER                        // Move to vertical center
};

enum HorizontalDirection { 
   LEFT,                              // Move to leftmost position
   RIGHT,                             // Move to rightmost position
   HORIZ_CENTER                       // Move to horizontal center
};

/*
* Initial setup function - runs once
* Initializes servos and runs test sequence
*/
void setup() {
   initializeServos();
   runTestSequence();
}

/*
* Main program loop
* Empty since this is a one-time test sequence
*/
void loop() {
   // Test sequence runs once in setup(), so loop() is empty
}

/*
* Initializes servo objects and moves them to center position
*/
void initializeServos() {
   up_down_servo.attach(UP_DOWN_SERVO_PIN);
   left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);
   centerServos();
}

/*
* Centers both servos to their middle positions
*/
void centerServos() {
   moveServos(VERT_CENTER, HORIZ_CENTER);
}

/*
* Moves both servos to specified positions
* Parameters:
* vertDir: Desired vertical direction (UP/DOWN/VERT_CENTER)
* horizDir: Desired horizontal direction (LEFT/RIGHT/HORIZ_CENTER)
*/
void moveServos(VerticalDirection vertDir, HorizontalDirection horizDir) {
   int vertAngle = getVerticalAngle(vertDir);
   int horizAngle = getHorizontalAngle(horizDir);
   
   up_down_servo.write(vertAngle);
   left_right_servo.write(horizAngle);
   delay(DELAY_TIME);
}

/*
* Converts vertical direction enum to corresponding angle
* Parameters:
* dir: Desired vertical direction
* Returns: Corresponding angle in degrees
*/
int getVerticalAngle(VerticalDirection dir) {
   switch(dir) {
       case UP: return UP_ANGLE;
       case DOWN: return DOWN_ANGLE;
       case VERT_CENTER: return VERT_CENTER_ANGLE;
       default: return VERT_CENTER_ANGLE;
   }
}

/*
* Converts horizontal direction enum to corresponding angle
* Parameters:
* dir: Desired horizontal direction
* Returns: Corresponding angle in degrees
*/
int getHorizontalAngle(HorizontalDirection dir) {
   switch(dir) {
       case LEFT: return LEFT_ANGLE;
       case RIGHT: return RIGHT_ANGLE;
       case HORIZ_CENTER: return HORIZ_CENTER_ANGLE;
       default: return HORIZ_CENTER_ANGLE;
   }
}

/*
* Executes complete test sequence of all movement patterns
*/
void runTestSequence() {
   moveLeftRight();
   moveUpDown();
   moveDiagonalTopLeftBottomRight();
   moveDiagonalTopRightBottomLeft();
}

/*
* Performs left-right movement pattern
* Keeps vertical position centered while moving horizontally
*/
void moveLeftRight() {
   for (int i = 0; i < NUM_ITERATIONS; i++) {
       moveServos(VERT_CENTER, LEFT);
       moveServos(VERT_CENTER, RIGHT);
   }
   centerServos();
}

/*
* Performs up-down movement pattern
* Keeps horizontal position centered while moving vertically
*/
void moveUpDown() {
   for (int i = 0; i < NUM_ITERATIONS; i++) {
       moveServos(UP, HORIZ_CENTER);
       moveServos(DOWN, HORIZ_CENTER);
   }
   centerServos();
}

/*
* Performs diagonal movement from top-left to bottom-right
*/
void moveDiagonalTopLeftBottomRight() {
   for (int i = 0; i < NUM_ITERATIONS; i++) {
       moveServos(UP, LEFT);
       moveServos(DOWN, RIGHT);
   }
   centerServos();
}

/*
* Performs diagonal movement from top-right to bottom-left
*/
void moveDiagonalTopRightBottomLeft() {
   for (int i = 0; i < NUM_ITERATIONS; i++) {
       moveServos(UP, RIGHT);
       moveServos(DOWN, LEFT);
   }
   centerServos();
}