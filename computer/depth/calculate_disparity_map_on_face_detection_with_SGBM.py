"""
Stereo Vision Depth Testing Script
Tests depth perception using two ESP32-CAMs for stereo vision
Features:
- Face-triggered disparity map calculation
- Real-time stereo parameter adjustment
- Camera configuration management
- Image rectification and 3D reprojection
- Performance monitoring
"""

import os
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
import mediapipe as mp

# Network and camera configuration
USE_HOTSPOT = False
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
STREAM_TIMEOUT = 3  # seconds

# Camera settings
JPEG_QUALITY = 12                # 0-63, lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution

# Stereo vision parameters
STEREO_BLOCK_SIZE = 11          # Must be odd
MIN_DISPARITY = 0
NUM_DISPARITIES = 5 * 16        # Must be divisible by 16
SPECKLE_WINDOW_SIZE = 0
SPECKLE_RANGE = 2
MODE = cv2.STEREO_SGBM_MODE_HH
UNIQUENESS_RATIO = 0
PRE_FILTER_CAP = 0
DISP12MAX_DIFF = 32

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

# Initialize stereo matcher with default parameters
stereo = cv2.StereoSGBM_create(
   minDisparity=MIN_DISPARITY,
   numDisparities=NUM_DISPARITIES,
   blockSize=STEREO_BLOCK_SIZE,
   P1=8 * STEREO_BLOCK_SIZE**2,
   P2=32 * STEREO_BLOCK_SIZE**2,
   disp12MaxDiff=DISP12MAX_DIFF,
   preFilterCap=PRE_FILTER_CAP,
   uniquenessRatio=UNIQUENESS_RATIO,
   speckleWindowSize=SPECKLE_WINDOW_SIZE,
   speckleRange=SPECKLE_RANGE,
   mode=MODE
)

# Initialize MediaPipe face detector
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Trackbar callback functions for real-time parameter adjustment
def on_min_disparity_change(val):
   global stereo
   stereo.setMinDisparity(val)

def on_num_disparities_change(val):
   global stereo
   stereo.setNumDisparities(max(16, (val // 16) * 16))

def on_block_size_change(val):
   global stereo
   stereo.setBlockSize(val if val % 2 == 1 else val + 1)

def on_speckle_window_size_change(val):
   global stereo
   stereo.setSpeckleWindowSize(val)

def on_speckle_range_change(val):
   global stereo
   stereo.setSpeckleRange(val)

def on_mode_change(val):
   global stereo
   stereo.setMode(cv2.STEREO_SGBM_MODE_HH if val == 0 else cv2.STEREO_SGBM_MODE_SGBM_3WAY)

def on_uniqueness_ratio_change(val):
   global stereo
   stereo.setUniquenessRatio(val)

def on_pre_filter_cap_change(val):
   global stereo
   stereo.setPreFilterCap(val)

def on_disp12max_diff_change(val):
   global stereo
   stereo.setDisp12MaxDiff(val)

# Create window and trackbars for parameter adjustment
cv2.namedWindow("Disparity map")
cv2.createTrackbar("Min Disp.", "Disparity map", MIN_DISPARITY, 32, on_min_disparity_change)
cv2.createTrackbar("Num Disp.", "Disparity map", NUM_DISPARITIES, 16 * 10, on_num_disparities_change)
cv2.createTrackbar("Block Size", "Disparity map", STEREO_BLOCK_SIZE, 13, on_block_size_change)
cv2.createTrackbar("Speckle Win", "Disparity map", SPECKLE_WINDOW_SIZE, 200, on_speckle_window_size_change)
cv2.createTrackbar("Speckle Range", "Disparity map", SPECKLE_RANGE, 100, on_speckle_range_change)
cv2.createTrackbar("Mode", "Disparity map", 0, 1, on_mode_change)
cv2.createTrackbar("Uniq. Ratio", "Disparity map", UNIQUENESS_RATIO, 60, on_uniqueness_ratio_change)
cv2.createTrackbar("Pre Filter Cap", "Disparity map", PRE_FILTER_CAP, 100, on_pre_filter_cap_change)
cv2.createTrackbar("Disp12MaxDiff", "Disparity map", DISP12MAX_DIFF, 60, on_disp12max_diff_change)

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
   """
   data = {'jpeg_quality': jpeg_quality, 'frame_size': frame_size}
   headers = {'Content-Type': 'application/x-www-form-urlencoded'}
   try:
       response = requests.post(esp32_config_url, data=data, headers=headers)
       print(f"Response from ESP32: {response.text}")
   except requests.RequestException as e:
       print(f"Error sending request: {e}")

def get_face_centroid(image):
   """
   Detects face in image and returns its centroid coordinates
   
   Args:
       image: Input image (BGR format)
   
   Returns:
       tuple: (x, y) coordinates of face centroid or None if no face detected
   """
   # Convert to RGB for MediaPipe
   image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
   results = face_detection.process(image_rgb)
   
   if results.detections:
       # Use first detected face's bounding box
       detection = results.detections[0]
       bboxC = detection.location_data.relative_bounding_box
       x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height
       return (x + w / 2, y + h / 2)
   return None

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
   thread_left.join()
   thread_right.join()

   return queue_left[0], queue_right[0]

def rectify_images(img_left, img_right):
   """
   Applies stereo rectification to image pair
   
   Args:
       img_left: Left camera image
       img_right: Right camera image
   
   Returns:
       tuple: (rectified_left, rectified_right)
   """
   # Apply rectification maps to both images
   img_left_rectified = cv2.remap(img_left, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
   img_right_rectified = cv2.remap(img_right, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
   return img_left_rectified, img_right_rectified

def calculate_disparity_maps(stereo, left_img_rectified, right_img_rectified):
   """
   Computes disparity map and 3D points from rectified stereo pair
   
   Args:
       stereo: StereoSGBM matcher object
       left_img_rectified: Rectified left image
       right_img_rectified: Rectified right image
   
   Returns:
       tuple: (normalized_disparity_map, 3D_points)
   """
   # Compute disparity map
   disparity = stereo.compute(left_img_rectified, right_img_rectified)
   
   # Normalize for visualization
   disp_norm = cv2.normalize(disparity, None, alpha=0, beta=255, 
                           norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
   
   # Calculate 3D coordinates
   points_3D = cv2.reprojectImageTo3D(disparity, Q)
   
   return disp_norm, points_3D

def main():
   """
   Main execution loop:
   1. Configures cameras
   2. Captures stereo images
   3. Detects faces
   4. Computes disparity maps when faces detected
   5. Tracks performance metrics
   """
   # Performance tracking
   total_face_time = 0
   total_disparity_map_time = 0
   face_iterations = 0
   disparity_map_iterations = 0
   
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
       
       # Capture and process stereo images
       img_left, img_right = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

       if img_left is not None and img_right is not None:
           stream_active = True
           img_left_rectified, img_right_rectified = rectify_images(img_left, img_right)

           # Detect faces and measure timing
           face_start = time.time()
           left_centroid = get_face_centroid(img_left_rectified)
           right_centroid = get_face_centroid(img_right_rectified)
           face_end = time.time()
           face_iterations += 1
           total_face_time += (face_end - face_start)

           # Calculate disparity if faces detected
           if left_centroid is not None and right_centroid is not None:
               disparity_start = time.time()
               disp_norm, points_3D = calculate_disparity_maps(
                   stereo, img_left_rectified, img_right_rectified)
               disparity_end = time.time()
               disparity_map_iterations += 1
               total_disparity_map_time += (disparity_end - disparity_start)
               
               # Display disparity map
               cv2.imshow("Disparity map", disp_norm)
               if cv2.waitKey(50) & 0xFF == ord('q'):
                   break
       else:
           print("One or both images are None.")
           stream_to_recover = True
           cv2.waitKey(1000)
           continue

   # Report performance metrics
   average_face_time = total_face_time / face_iterations
   average_disparity_map_time = total_disparity_map_time / disparity_map_iterations
   print(f"\nAverage face centroid calculation time over {face_iterations} iterations: {average_face_time:.3f} seconds")
   print(f"Average disparity map calculation time over {disparity_map_iterations} iterations: {average_disparity_map_time:.3f} seconds")

if __name__ == "__main__":
   main()