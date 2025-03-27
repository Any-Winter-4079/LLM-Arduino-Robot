"""
Depth Perception Using Depth Anything
Tests depth perception using ESP32-CAMs with Depth Anything neural network
Features:
- Real-time monocular depth estimation
- Camera configuration management
- Image rectification
- Performance monitoring
- Automatic stream recovery
- Support for dual camera setup with failover
"""

import os
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
from depth_anything.run import get_depth
from depth_anything.depth_anything.dpt import DepthAnything
from depth_anything.metric_depth.zoedepth.utils.geometry import depth_to_points

# Configuration
JPEG_QUALITY = 12                # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution
USE_HOTSPOT = False
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
STREAM_TIMEOUT = 3               # seconds
CONFIG_TIMEOUT = 5               # seconds

# Camera endpoints
esp32_right_image_url = f"http://{RIGHT_EYE_IP}/image.jpg"
esp32_left_image_url = f"http://{LEFT_EYE_IP}/image.jpg"
esp32_left_config_url = f"http://{LEFT_EYE_IP}/camera_config"
esp32_right_config_url = f"http://{RIGHT_EYE_IP}/camera_config"

# Load stereo calibration maps
stereo_maps_dir = '../undistortion_and_rectification/stereo_maps'
stereoMapL_x = np.load(os.path.join(stereo_maps_dir, 'stereoMapL_x.npy'))
stereoMapL_y = np.load(os.path.join(stereo_maps_dir, 'stereoMapL_y.npy'))
stereoMapR_x = np.load(os.path.join(stereo_maps_dir, 'stereoMapR_x.npy'))
stereoMapR_y = np.load(os.path.join(stereo_maps_dir, 'stereoMapR_y.npy'))
Q = np.load(os.path.join(stereo_maps_dir, 'Q.npy'))

# Initialize Depth Anything model
encoder = 'vits'                 # can also be 'vitb' or 'vitl'
depth_anything = DepthAnything.from_pretrained('LiheYoung/depth_anything_{:}14'.format(encoder))

def fetch_image_with_timeout(url, queue, timeout=STREAM_TIMEOUT):
    """
    Fetches an image from a camera URL with timeout protection
    
    Args:
        url: Camera stream URL
        queue: Queue to store retrieved image
        timeout: Maximum wait time in seconds
    """
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        img_np = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        queue.append(img)
    except Exception as e:
        print(f"Timeout or error fetching image from {url}: {e}")
        queue.append(None)

def update_camera_config(esp32_config_url, jpeg_quality, frame_size):
    """
    Updates camera configuration via HTTP POST
    
    Args:
        esp32_config_url: Camera configuration endpoint
        jpeg_quality: JPEG compression quality (0-63)
        frame_size: Resolution setting (e.g., "FRAMESIZE_VGA")
        
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    data = {'jpeg_quality': jpeg_quality, 'frame_size': frame_size}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(esp32_config_url, data=data, headers=headers, timeout=CONFIG_TIMEOUT)
        print(f"Response from ESP32: {response.text}")
        return True
    except requests.RequestException as e:
        print(f"Error sending request: {e}")
        return False

def get_stereo_images(url_left, url_right):
    """
    Captures synchronized images from both cameras
    
    Args:
        url_left: Left camera URL
        url_right: Right camera URL
    
    Returns:
        tuple: (left_image, right_image)
    """
    queue_left, queue_right = [], []

    # Start parallel image capture threads
    thread_left = threading.Thread(target=fetch_image_with_timeout, args=(url_left, queue_left))
    thread_right = threading.Thread(target=fetch_image_with_timeout, args=(url_right, queue_right))
    
    thread_left.start()
    thread_right.start()
    
    # Wait for both threads to finish
    thread_left.join()
    thread_right.join()

    # Retrieve images from the queues
    img_left = queue_left[0]
    img_right = queue_right[0]

    return img_left, img_right

def rectify_left_image(image):
    """
    Applies stereo rectification to left camera image
    
    Args:
        image: Left camera image
    
    Returns:
        ndarray: Rectified left image
    """
    image_rectified = cv2.remap(image, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
    return image_rectified

def rectify_right_image(image):
    """
    Applies stereo rectification to right camera image
    
    Args:
        image: Right camera image
    
    Returns:
        ndarray: Rectified right image
    """
    image_rectified = cv2.remap(image, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
    return image_rectified

def main():
    """
    Main execution loop:
    1. Configures cameras
    2. Captures images from available cameras
    3. Applies image rectification
    4. Computes depth maps using Depth Anything
    5. Tracks performance metrics
    """
    # Performance tracking
    total_depth_time = 0
    depth_iterations = 0
    
    # Stream state tracking
    stream_to_recover = False
    stream_active = False
    
    # Initialize camera configurations
    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    while True:
        # Handle stream recovery if needed
        if stream_to_recover and stream_active:
            print("Stream is being recovered.")
            update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
            update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False
        
        # Fetch images from both cameras
        img_right, img_left = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        # Select available image for processing with fallback
        if img_right is not None:
            img_rectified = rectify_right_image(img_right)
        elif img_left is not None:
            img_rectified = rectify_left_image(img_left)
        else:
            print("Both images are None.")
            stream_to_recover = True
            # Wait for the camera to recover
            cv2.waitKey(1000)
            continue

        stream_active = True

        # Compute depth map and measure timing
        depth_start = time.time()
        depth = get_depth(img_rectified)
        depth_end = time.time()
        depth_iterations += 1
        total_depth_time += (depth_end - depth_start)
        
        # Display depth map
        cv2.imshow("Stereo depth", depth)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break
    
    # Report performance metrics
    average_depth_time = total_depth_time / depth_iterations
    print(f"Average depth calculation time over {depth_iterations} iterations: {average_depth_time:.3f} seconds")

if __name__ == "__main__":
    main()