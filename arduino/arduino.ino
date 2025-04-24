#include <Mouse.h>

/* 
    --- Tutorial ---

    This code uses an Arduino to control a mouse. It listens for commands over the serial port, which are used to:
    - Move the mouse (command format: "M{x,y}").
    - Simulate a mouse click (command format: "C").

    --- Steps to use ---
    1. Upload this code to your Arduino board (e.g., Arduino Leonardo or similar that supports Mouse library).
    2. Establish a serial connection with the Arduino (via USB or Bluetooth).
    3. Send commands through the serial port:
        - "M{x,y}" -> Move the mouse by {x} pixels in the x direction and {y} pixels in the y direction.
        - "C" -> Simulate a mouse click.
    4. The code can be modified to handle different types of mouse movements or additional actions.
    
    --- Variables ---
    - `deltaX` and `deltaY`: Store the x and y movement for the mouse.
    - `isClicking`: A flag to indicate if the mouse is currently clicking.
    - `clickStartTime`: A timestamp that marks the beginning of a mouse click.
    - `clickDuration`: A randomly generated duration for the click action.

*/

String command = "";  // The command received from the serial buffer
int deltaX = 0, deltaY = 0;  // Movement values for the X and Y axes

// Click state management
bool isClicking = false;  // Tracks whether a mouse click is currently happening
unsigned long clickStartTime = 0;  // Marks the time when the click begins
unsigned long clickDuration;  // Specifies how long the click will last in milliseconds

void setup() {
    Serial.begin(115200);  // Initialize serial communication at a baud rate of 115200
    Serial.setTimeout(1);  // Set a short timeout for serial reads to prevent blocking
    Mouse.begin();  // Initialize mouse control
    
    randomSeed(analogRead(0));  // Seed the random number generator using an unconnected analog pin for better randomness
}

void loop() {
    if (Serial.available() > 0) {  // Check if there is a command waiting in the serial buffer
        command = Serial.readStringUntil('\n');  // Read the incoming command until a newline character
        command.trim();  // Clean up any leading or trailing spaces

        if (command.startsWith("M")) {  // If the command starts with 'M', it's a mouse movement command
            int commaIndex = command.indexOf(',');  // Find the position of the comma
            if (commaIndex != -1) {  // Ensure the command is formatted correctly
                deltaX = command.substring(1, commaIndex).toInt();  // Get X-axis movement
                deltaY = command.substring(commaIndex + 1).toInt();  // Get Y-axis movement

                // Move the mouse incrementally to prevent sudden jumps
                while (deltaX != 0 || deltaY != 0) {
                    int moveX = constrain(deltaX, -128, 127);  // Limit X movement to avoid overflow
                    int moveY = constrain(deltaY, -128, 127);  // Limit Y movement similarly
                    Mouse.move(moveX, moveY);  // Perform the mouse movement
                    deltaX -= moveX;  // Decrease remaining movement for X-axis
                    deltaY -= moveY;  // Decrease remaining movement for Y-axis
                }
            }
        }
        else if (command.startsWith("C")) {  // If the command starts with 'C', it's a mouse click command
            if (!isClicking) {  // If we're not already clicking
                Mouse.press(MOUSE_LEFT);  // Press the left mouse button down
                clickStartTime = millis();  // Record the current time as the start of the click
                clickDuration = random(40, 80);  // Choose a random click duration between 40ms and 80ms
                isClicking = true;  // Mark that we're in a clicking state
            }
        }
    }

    if (isClicking) {  // If a click is ongoing, check if it's time to release the button
        if (millis() - clickStartTime >= clickDuration) {  // If the specified click duration has passed
            Mouse.release(MOUSE_LEFT);  // Release the left mouse button
            isClicking = false;  // Reset the clicking state
        }
    }
}
