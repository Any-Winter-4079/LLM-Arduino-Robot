import requests
from typing import Dict, Union

# Configurations
USE_HOTSPOT = True
IP = "172.20.10.12" if USE_HOTSPOT else "192.168.1.182"

def move_motors(ip: str, left_direction: str, right_direction: str, speed: int) -> Dict[str, Union[bool, str]]:
    """
    Send a request to move the motors with the specified directions and speed.

    Args:
        ip (str): IP address of the ESP32-WROVER.
        left_direction (str): Direction of the left motor ('10': forward, '01': backward, '00': stop).
        right_direction (str): Direction of the right motor ('10': forward, '01': backward, '00': stop).
        speed (int): Speed of the motors (0-255).

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing the success status and response message.
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
    Get and validate user input for motor directions and speed.

    Returns:
        tuple: Left motor direction, right motor direction, and speed.

    Raises:
        ValueError: If input is invalid.
        SystemExit: If user wants to exit.
    """
    user_input = input("Enter left motor direction, right motor direction, and speed separated by spaces ('10'/'01'/'00' for directions, 0-255 for speed) or 'exit' to quit: ")
    
    if user_input.lower() == 'exit':
        raise SystemExit
    
    left_direction, right_direction, speed = user_input.split()
    speed = int(speed)
    
    if not (left_direction in ['10', '01', '00'] and right_direction in ['10', '01', '00'] and 0 <= speed <= 255):
        raise ValueError("Directions must be '10', '01', or '00', and speed must be between 0 and 255.")
    
    return left_direction, right_direction, speed

def main():
    """Main function to run the motor control program."""
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