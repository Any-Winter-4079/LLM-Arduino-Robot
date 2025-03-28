"""
Stereo Camera Calibration Image Capture
Captures synchronized image pairs from dual ESP32-CAMs for stereo vision calibration
Features:
- Simultaneous image capture from left and right cameras
- Camera configuration control (resolution, quality)
- Interactive image saving with visual preview
- Structured file organization for calibration workflow
- Multi-threaded image acquisition for improved synchronization
"""

import os
import cv2
import requests
import threading
import numpy as np
import urllib.request
from datetime import datetime

# Network configuration
USE_HOTSPOT = False  # True for phone hotspot, False for home WiFi
IP_LEFT = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"  # Left eye (AI-Thinker ESP32-CAM)
IP_RIGHT = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"  # Right eye (M5Stack Wide ESP32-CAM)

# Camera settings
JPEG_QUALITY = 6  # 0-63, lower means higher quality (12 recommended for production)
FRAME_SIZE = "FRAMESIZE_VGA"  # 640x480 (also used in production)

# Image endpoints
ESP32_RIGHT_IMAGE_URL = f"http://{IP_RIGHT}/image.jpg"
ESP32_LEFT_IMAGE_URL = f"http://{IP_LEFT}/image.jpg"
ESP32_LEFT_CONFIG_URL = f"http://{IP_LEFT}/camera_config"
ESP32_RIGHT_CONFIG_URL = f"http://{IP_RIGHT}/camera_config"

# Storage paths
SAVE_PATH_RIGHT = "./images/right_eye"
SAVE_PATH_LEFT = "./images/left_eye"

# Capture parameters
FRAME_INTERVAL = 3  # Seconds to wait between frames (time to press 's')
NUM_IMAGES = 100  # Total number of image pairs to attempt capturing


def update_camera_config(esp32_config_url, jpeg_quality, frame_size):
    """
    Updates ESP32-CAM configuration via HTTP POST request
    
    Args:
        esp32_config_url: Configuration endpoint URL
        jpeg_quality: JPEG compression level (0-63, lower is better)
        frame_size: Resolution identifier (e.g., "FRAMESIZE_VGA")
    """
    data = {'jpeg_quality': jpeg_quality, 'frame_size': frame_size}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(esp32_config_url, data=data, headers=headers)
        print(f"Response from ESP32: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending configuration request: {e}")


def fetch_image(url, queue):
    """
    Fetches a camera image in a separate thread
    
    Args:
        url: ESP32-CAM image endpoint URL
        queue: List to store the retrieved image
    """
    try:
        resp = urllib.request.urlopen(url)
        img_np = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        queue.append(img)
    except urllib.error.URLError as e:
        print(f"Error fetching image from {url}: {e}")
        queue.append(None)


def capture_stereo_images(url_left, url_right, save_path_left, save_path_right):
    """
    Captures and optionally saves synchronized image pairs from both cameras
    
    Args:
        url_left: Left camera image endpoint
        url_right: Right camera image endpoint
        save_path_left: Directory path for left camera images
        save_path_right: Directory path for right camera images
        
    Returns:
        bool: True if images were saved (user pressed 's'), False otherwise
    """
    queue_left, queue_right = [], []

    # Start threads for parallel image capture
    thread_left = threading.Thread(target=fetch_image, args=(url_left, queue_left))
    thread_right = threading.Thread(target=fetch_image, args=(url_right, queue_right))
    
    thread_left.start()
    thread_right.start()

    # Wait for both threads to complete
    thread_left.join()
    thread_right.join()

    # Retrieve images from the queues
    img_left, img_right = queue_left[0], queue_right[0]

    # Display preview of both images side-by-side
    if img_left is not None and img_right is not None:
        combined_image = cv2.hconcat([img_right, img_left])
        cv2.imshow("Stereo Cameras", combined_image)
    else:
        print("Error: Failed to retrieve one or both camera images")
    
    key = cv2.waitKey(FRAME_INTERVAL * 1000)

    # Save images if user presses 's'
    if key == ord('s'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_filename_left = os.path.join(save_path_left, f"stereo_image_{timestamp}.jpg")
        save_filename_right = os.path.join(save_path_right, f"stereo_image_{timestamp}.jpg")
        cv2.imwrite(save_filename_left, img_left)
        cv2.imwrite(save_filename_right, img_right)
        print(f"Saved {save_filename_left} and {save_filename_right}")
        return True
    return False


def main():
    """
    Main execution function:
    1. Creates storage directories if needed
    2. Configures both cameras with desired settings
    3. Captures image pairs with interactive saving
    4. Continues until all pairs are processed
    """
    # Ensure the save directories exist
    os.makedirs(SAVE_PATH_LEFT, exist_ok=True)
    os.makedirs(SAVE_PATH_RIGHT, exist_ok=True)

    # Update the camera configurations
    update_camera_config(ESP32_LEFT_CONFIG_URL, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(ESP32_RIGHT_CONFIG_URL, JPEG_QUALITY, FRAME_SIZE)

    print("\nStereo Calibration Image Capture")
    print("--------------------------------")
    print("Instructions:")
    print("1. Hold the chessboard pattern in view of both cameras")
    print("2. Press 's' to save the current image pair")
    print("3. Move the chessboard to a different position/angle")
    print("4. Continue until you have sufficient calibration images")
    print("\nStarting capture sequence...\n")

    # Capture images
    saved_count = 0
    for i in range(NUM_IMAGES):
        print(f"Pair {i+1}/{NUM_IMAGES}: Position chessboard and wait for preview...")
        saved = capture_stereo_images(ESP32_LEFT_IMAGE_URL, ESP32_RIGHT_IMAGE_URL, 
                                     SAVE_PATH_LEFT, SAVE_PATH_RIGHT)
        if saved:
            saved_count += 1
            print(f"Pair {i+1} saved ({saved_count} total). Capturing next pair.")
        else:
            print(f"Pair {i+1} not saved. Capturing next pair.")

    cv2.destroyAllWindows()
    print(f"\nStereo image capturing completed. {saved_count} image pairs saved.")


if __name__ == "__main__":
    main()