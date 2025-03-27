"""
Stereo Face Recognition System
Recognizes faces using stereo camera setup with DeepFace
Features:
- Real-time face detection and recognition
- Camera configuration management
- Image rectification
- Automatic stream recovery with failover
- Visual display with bounding boxes and name labels
- Performance monitoring
- Customizable recognition parameters
"""

import os
import re
import cv2
import time
import requests
import threading
import numpy as np
import urllib.request
from deepface import DeepFace

# Configuration
JPEG_QUALITY = 12                # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution
USE_HOTSPOT = False
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
STREAM_TIMEOUT = 3               # seconds
CONFIG_TIMEOUT = 5               # seconds

# Face recognition settings
DATABASE_PATH = "production_database"
DISTANCE_METRIC = "cosine"       # Options: cosine, euclidean, euclidean_l2
BACKEND = "fastmtcnn"           # Detection backend
MODEL = "VGG-Face"               # Recognition model
THRESHOLD = 0.625                # Recognition threshold

# Note different metrics require different thresholds
# The defaults are:
# | Model       | Cosine | Euclidean | Euclidean L2 |
# |-------------|--------|-----------|--------------|
# | VGG-Face    | 0.68   | 1.17      | 1.17         |
# | Facenet     | 0.40   | 10        | 0.80         |
# | Facenet512  | 0.30   | 23.56     | 1.04         |
# | ArcFace     | 0.68   | 4.15      | 1.13         |
# | Dlib        | 0.07   | 0.6       | 0.4          |
# | SFace       | 0.593  | 10.734    | 1.055        |
# | OpenFace    | 0.10   | 0.55      | 0.55         |
# | DeepFace    | 0.23   | 64        | 0.64         |
# | DeepID      | 0.015  | 45        | 0.17         |

# For my case: 0.625, cosine, fastmtcnn, and VGG-Face worked well but you should experiment with different combinations.

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


def draw_boxes_and_labels(img_rectified, unique_individuals):
    """
    Draws bounding boxes and name labels for recognized faces
    
    Args:
        img_rectified: Rectified image to draw on
        unique_individuals: Dictionary of recognized individuals with their info
    """
    for person_name, info in unique_individuals.items():
        # Extract face coordinates
        x, y, w, h = info['source_x'], info['source_y'], info['source_w'], info['source_h']
        
        # Format the display name by removing numbers and underscores
        identity = person_name
        identity = re.sub(r'_\d+$', '', identity)
        identity = identity.replace('_', ' ')
        
        # Draw bounding box and name label
        cv2.rectangle(img_rectified, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img_rectified, identity, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


def get_top_predictions(dfs_list):
    """
    Extracts the top prediction for each detected face
    
    Args:
        dfs_list: List of dataframes containing recognition results
    
    Returns:
        list: Top prediction for each detected face
    """
    top_predictions = []
    for df in dfs_list:
        if len(df) > 0:
            top_prediction = df.iloc[0]
            top_predictions.append(top_prediction)
    return top_predictions


def process_predictions(top_predictions):
    """
    Processes predictions to extract unique individuals
    
    Args:
        top_predictions: List of top predictions for each face
    
    Returns:
        dict: Dictionary of unique individuals with their info
    """
    unique_individuals = {}
    for prediction in top_predictions:
        # Extract person name from identity path
        identity_path = prediction['identity'].replace(DATABASE_PATH + '/', '').split('/')
        person_name = identity_path[0]
        
        # Store first occurrence of each person
        if person_name not in unique_individuals:
            unique_individuals[person_name] = prediction
    return unique_individuals


def recognize_face(test_image_path):
    """
    Recognizes faces in an image using DeepFace
    
    Args:
        test_image_path: Path or array of image for recognition
    
    Returns:
        dict: Dictionary of unique individuals with their info
    """
    try:
        # Perform face recognition
        dfs = DeepFace.find(
            img_path=test_image_path,
            db_path=DATABASE_PATH,
            model_name=MODEL,
            detector_backend=BACKEND,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=False,
            threshold=THRESHOLD)
        
        # Process the results
        top_predictions = get_top_predictions(dfs)
        unique_individuals = process_predictions(top_predictions)
        return unique_individuals
    except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {MODEL} and backend {BACKEND}: {e}\n")
        return None


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

    thread_left.join()
    thread_right.join()

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
    4. Performs face recognition
    5. Displays results with bounding boxes
    6. Tracks performance metrics
    """
    # Performance tracking
    total_face_rec_time = 0
    face_rec_iterations = 0
    
    # Stream state tracking
    stream_to_recover = False
    stream_active = False

    # Initialize camera configurations
    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    # Pre-build model for faster recognition
    DeepFace.build_model(MODEL)

    while True:
        # Handle stream recovery if needed
        if stream_to_recover and stream_active:
            print("Stream recovered.")
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
            cv2.waitKey(2000)  # Wait for the camera to recover
            continue

        stream_active = True

        # Perform face recognition and measure timing
        face_rec_start = time.time()
        result = recognize_face(img_rectified)
        face_rec_end = time.time()
        face_rec_iterations += 1
        total_face_rec_time += (face_rec_end - face_rec_start)
        
        # Draw recognition results on image
        if result is not None:
            draw_boxes_and_labels(img_rectified, result)
        
        # Display the result
        cv2.imshow("Stereo face_rec", img_rectified)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    # Report performance metrics
    average_face_rec_time = total_face_rec_time / face_rec_iterations
    print(f"Average face_rec calculation time over {face_rec_iterations} iterations: {average_face_rec_time:.3f} seconds")


if __name__ == "__main__":
    main()