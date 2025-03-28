"""
Motor Control Test Script
Controls robot's DC motors via ESP32-WROVER for movement
Features:
- Independent left/right motor control
- Forward/backward/stop commands
- Variable speed control
- Network communication with ESP32-WROVER
- Error handling for network and input issues
"""
import requests

# Network configuration 
USE_HOTSPOT = True                                         # True for phone hotspot, False for home WiFi
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"    # ESP32-WROVER's IP address

def move_motors(ip, left_direction, right_direction, speed):
   """
   Sends HTTP POST request to ESP32-WROVER to control motors
   
   Args:
       ip: IP address of ESP32-WROVER
       left_direction: Left motor direction code
           '10': forward
           '01': backward
           '00': stop
       right_direction: Right motor direction code
           '10': forward
           '01': backward  
           '00': stop
       speed: Motor speed (0-255)
   Returns:
       Dictionary containing:
       - success: True if request succeeded, False otherwise
       - message: Response text or error message
   """
   esp32_command_url = f"http://{ip}/command"
   data = {
       'leftMD': left_direction,
       'rightMD': right_direction,
       'motorsS': speed
   }
   headers = {'Content-Type': 'application/x-www-form-urlencoded'}
   
   try:
       response = requests.post(esp32_command_url, data=data, headers=headers)
       return {"success": True, "message": response.text}
   except requests.RequestException as e:
       return {"success": False, "message": str(e)}

def get_user_input():
   """
   Prompts for and validates motor control inputs
   
   Returns:
       tuple: (left_direction, right_direction, speed)
           left_direction, right_direction: '10', '01', or '00' 
           speed: 0-255
   Raises:
       ValueError: If directions or speed are invalid
       SystemExit: If user enters 'exit' 
   """
   user_input = input(
       "Enter left motor direction, right motor direction, and speed separated by spaces\n"
       "Directions: '10' (forward), '01' (backward), '00' (stop)\n"
       "Speed: 0-255\n"
       "Or enter 'exit' to quit: "
   )
   
   if user_input.lower() == 'exit':
       raise SystemExit
   
   left_direction, right_direction, speed = user_input.split()
   speed = int(speed)
   
   valid_directions = ['10', '01', '00']
   if not (left_direction in valid_directions and 
           right_direction in valid_directions and 
           0 <= speed <= 255):
       raise ValueError(
           "Directions must be '10' (forward), '01' (backward), or '00' (stop), "
           "and speed must be between 0 and 255."
       )
   
   return left_direction, right_direction, speed

def main():
   """
   Main execution loop:
   1. Gets motor control inputs from user
   2. Sends movement commands to ESP32-WROVER
   3. Displays results or error messages
   4. Continues until user exits
   """
   while True:
       try:
           left_direction, right_direction, speed = get_user_input()
           result = move_motors(IP, left_direction, right_direction, speed)
           if result["success"]:
               print(f"Response from ESP32: {result['message']}")
           else:
               print(f"Error sending request: {result['message']}")
       except ValueError as e:
           print(f"Invalid input: {e}")
       except SystemExit:
           break

if __name__ == "__main__":
   main()