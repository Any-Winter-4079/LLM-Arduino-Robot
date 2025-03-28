"""
Servo Control Test Script
Controls robot's servo motors via ESP32-WROVER for eye movement
Features:
- Vertical (up/down) and horizontal (left/right) servo control
- Input validation for servo angle constraints
- Network communication with ESP32-WROVER
- Error handling for network and input issues
"""

import requests

# Network configuration
USE_HOTSPOT = True                                         # True for phone hotspot, False for home WiFi
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"    # ESP32-WROVER's IP address

# Servo angle constraints (in degrees)
DOWN_ANGLE = 50    # Lowest vertical position 
UP_ANGLE = 110     # Highest vertical position
LEFT_ANGLE = 120   # Leftmost position
RIGHT_ANGLE = 60   # Rightmost position

def move_servos(ip, angle_vp, angle_hp):
   """
   Sends HTTP POST request to ESP32-WROVER to move servos to specified angles
   
   Args:
       ip: IP address of ESP32-WROVER
       angle_vp: Vertical position angle (50-110 degrees)
       angle_hp: Horizontal position angle (60-120 degrees)

   Returns:
       Dictionary containing:
       - success: True if request succeeded, False otherwise
       - message: Response text or error message
   """
   esp32_command_url = f"http://{ip}/command"
   data = {'angleVP': angle_vp, 'angleHP': angle_hp}
   headers = {'Content-Type': 'application/x-www-form-urlencoded'}
   
   try:
       response = requests.post(esp32_command_url, data=data, headers=headers)
       return {"success": True, "message": response.text}
   except requests.RequestException as e:
       return {"success": False, "message": str(e)}

def get_user_input():
   """
   Prompts for and validates servo angle inputs
   
   Returns:
       tuple: (vertical_angle, horizontal_angle)
       
   Raises:
       ValueError: If angles are outside valid ranges
       SystemExit: If user enters 'exit'
   """
   user_input = input(f"Enter vertical ({DOWN_ANGLE}-{UP_ANGLE}) and horizontal ({RIGHT_ANGLE}-{LEFT_ANGLE}) servo angles separated by a space, or 'exit' to quit: ")
   
   if user_input.lower() == 'exit':
       raise SystemExit
   
   angle_vp, angle_hp = map(int, user_input.split())
   
   if not (DOWN_ANGLE <= angle_vp <= UP_ANGLE and RIGHT_ANGLE <= angle_hp <= LEFT_ANGLE):
       raise ValueError(f"Vertical angle must be between {DOWN_ANGLE} and {UP_ANGLE}, and horizontal angle must be between {RIGHT_ANGLE} and {LEFT_ANGLE}.")
   
   return angle_vp, angle_hp

def main():
   """
   Main execution loop:
   1. Gets servo angles from user
   2. Sends movement commands to ESP32-WROVER
   3. Displays results or error messages
   4. Continues until user exits
   """
   while True:
       try:
           angle_vp, angle_hp = get_user_input()
           result = move_servos(IP, angle_vp, angle_hp)
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