import requests
from typing import Dict, Union

# Configurations
USE_HOTSPOT = True
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"

# Servo angle constraints
DOWN_ANGLE = 50
UP_ANGLE = 110
LEFT_ANGLE = 120
RIGHT_ANGLE = 60

def move_servos(ip: str, angle_vp: int, angle_hp: int) -> Dict[str, Union[bool, str]]:
    """
    Send a request to move the servos to the specified angles.

    Args:
        ip (str): IP address of the ESP32-WROVER.
        angle_vp (int): Vertical angle (DOWN_ANGLE to UP_ANGLE).
        angle_hp (int): Horizontal angle (RIGHT_ANGLE to LEFT_ANGLE).

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing the success status and response message.
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
    Get and validate user input for servo angles.

    Returns:
        tuple: Vertical and horizontal angles.

    Raises:
        ValueError: If input is invalid.
        SystemExit: If user wants to exit.
    """
    user_input = input(f"Enter vertical ({DOWN_ANGLE}-{UP_ANGLE}) and horizontal ({RIGHT_ANGLE}-{LEFT_ANGLE}) servo angles separated by a space, or 'exit' to quit: ")
    
    if user_input.lower() == 'exit':
        raise SystemExit
    
    angle_vp, angle_hp = map(int, user_input.split())
    
    if not (DOWN_ANGLE <= angle_vp <= UP_ANGLE and RIGHT_ANGLE <= angle_hp <= LEFT_ANGLE):
        raise ValueError(f"Vertical angle must be between {DOWN_ANGLE} and {UP_ANGLE}, and horizontal angle must be between {RIGHT_ANGLE} and {LEFT_ANGLE}.")
    
    return angle_vp, angle_hp

def main():
    """Main function to run the servo control program."""
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