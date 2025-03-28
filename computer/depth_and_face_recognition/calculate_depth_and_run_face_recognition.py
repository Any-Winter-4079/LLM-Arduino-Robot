"""
Integrated Stereo Vision System
Combines face recognition, object detection, and depth estimation
Features:
- Real-time face recognition with DeepFace
- Object detection with YOLOv8
- Stereo depth mapping with adjustable parameters
- Camera configuration management
- Image rectification
- Automatic stream recovery with failover
- Dynamic visualization with depth information
- Multi-threaded image acquisition
"""

import os
import re
import cv2
import requests
import threading
import numpy as np
import urllib.request
import mediapipe as mp
from ultralytics import YOLO
from deepface import DeepFace

# Configuration
JPEG_QUALITY = 12                # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution
USE_HOTSPOT = False
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
STREAM_TIMEOUT = 3               # seconds

# Stereo vision parameters
STEREO_MAPS_DIR = '../undistortion_and_rectification/stereo_maps'
ALLOWED_DEPTH = 0.875
LABELS = ["bottle"]              # Object labels to track
STEREO_BLOCK_SIZE = 11           # Must be odd
MIN_DISPARITY = 8
NUM_DISPARITIES = 5 * 16         # Must be non-zero, divisible by 16
SPECKLE_WINDOW_SIZE = 0
SPECKLE_RANGE = 2
MODE = cv2.STEREO_SGBM_MODE_HH
UNIQUENESS_RATIO = 0
PRE_FILTER_CAP = 0
DISP12MAX_DIFF = 32

# Face recognition settings
DATABASE_PATH = "production_database"
DISTANCE_METRIC = "cosine"       # Options: cosine, euclidean, euclidean_l2
BACKEND = "fastmtcnn"            # Detection backend
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

# For my case: 0.625, cosine, fastmtcnn, and VGG-Face worked well but you should experiment with different combinations

# Camera endpoints
esp32_right_image_url = f"http://{RIGHT_EYE_IP}/image.jpg"
esp32_left_image_url = f"http://{LEFT_EYE_IP}/image.jpg"
esp32_left_config_url = f"http://{LEFT_EYE_IP}/camera_config"
esp32_right_config_url = f"http://{RIGHT_EYE_IP}/camera_config"

# Load stereo calibration maps
stereoMapL_x = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapL_x.npy'))
stereoMapL_y = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapL_y.npy'))
stereoMapR_x = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapR_x.npy'))
stereoMapR_y = np.load(os.path.join(STEREO_MAPS_DIR, 'stereoMapR_y.npy'))
Q = np.load(os.path.join(STEREO_MAPS_DIR, 'Q.npy'))

# Initialize stereo matcher
stereo = cv2.StereoSGBM_create(minDisparity=MIN_DISPARITY,
                               numDisparities=NUM_DISPARITIES,
                               blockSize=STEREO_BLOCK_SIZE,
                               P1=8 * STEREO_BLOCK_SIZE**2,
                               P2=32 * STEREO_BLOCK_SIZE**2,
                               disp12MaxDiff=DISP12MAX_DIFF,
                               preFilterCap=PRE_FILTER_CAP,
                               uniquenessRatio=UNIQUENESS_RATIO,
                               speckleWindowSize=SPECKLE_WINDOW_SIZE,
                               speckleRange=SPECKLE_RANGE,
                               mode=MODE)

# Initialize face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Initialize object detection
object_detection_model = YOLO("yolov8n.pt")

# Load object class names
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

#############################
# Stereo parameter controls #
#############################
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

# Create window and trackbars for stereo parameter adjustment
cv2.namedWindow("Disparity map")
cv2.createTrackbar("Min Disp.", "Disparity map", MIN_DISPARITY, 32, on_min_disparity_change)
cv2.createTrackbar("Num Disp.", "Disparity map", NUM_DISPARITIES, 16 * 16, on_num_disparities_change)
cv2.createTrackbar("Block Size", "Disparity map", STEREO_BLOCK_SIZE, 13, on_block_size_change)
cv2.createTrackbar("Speckle Win", "Disparity map", SPECKLE_WINDOW_SIZE, 200, on_speckle_window_size_change)
cv2.createTrackbar("Speckle Range", "Disparity map", SPECKLE_RANGE, 100, on_speckle_range_change)
cv2.createTrackbar("Mode", "Disparity map", 0, 1, on_mode_change)
cv2.createTrackbar("Uniq. Ratio", "Disparity map", UNIQUENESS_RATIO, 60, on_uniqueness_ratio_change)
cv2.createTrackbar("Pre Filter Cap", "Disparity map", PRE_FILTER_CAP, 100, on_pre_filter_cap_change)
cv2.createTrackbar("Disp12MaxDiff", "Disparity map", DISP12MAX_DIFF, 60, on_disp12max_diff_change)


def draw_boxes_and_labels(img_rectified, unique_individuals):
    """
    Draws bounding boxes and name labels for recognized faces
    
    Args:
        img_rectified: Rectified image to draw on
        unique_individuals: Dictionary of recognized individuals with their info
    """
    for person_name, info in unique_individuals.items():
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
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height
            centroid = (x + w / 2, y + h / 2)
            return centroid
    return None


def get_face_bounding_box(image):
    """
    Detects face in image and returns its bounding box
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        tuple: (x, y, w, h) coordinates of face or None if no face detected
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height
            height, width, _ = image.shape
            x, y, w, h = int(x * width), int(y * height), int(w * width), int(h * height)
            return (x, y, w, h)
    return None


def get_object_bounding_boxes(image, label_filter=None):
    """
    Detects objects in image and returns their bounding boxes and labels
    
    Args:
        image: Input image (BGR format)
        label_filter: List of object labels to detect (None for all objects)
    
    Returns:
        tuple: (list of bounding boxes, list of corresponding labels)
    """
    results = object_detection_model(image, device="mps")
    result = results[0]
    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    class_ids = np.array(result.boxes.cls.cpu(), dtype="int")
    
    filtered_bboxes = []
    filtered_labels = []
    
    for cls, bbox in zip(class_ids, bboxes):
        if label_filter is None or classes[cls] in label_filter:
            (x, y, x2, y2) = bbox
            filtered_bboxes.append((x, y, x2 - x, y2 - y))
            filtered_labels.append(classes[cls])
            
    return filtered_bboxes, filtered_labels


def calculate_average_depth(points_3D, bbox, allowed_depth=0.95):
    """
    Calculates average depth within a bounding box region
    
    Args:
        points_3D: 3D points map from stereo disparity
        bbox: Object bounding box (x, y, w, h)
        allowed_depth: Depth filter threshold (0.0-1.0)
    
    Returns:
        float: Average depth value or None if invalid
    """
    x, y, w, h = bbox
    obj_region = points_3D[y:y+h, x:x+w]
    
    # Get valid depth values
    valid_depths = obj_region[:, :, 2]
    valid_depths = valid_depths[np.isfinite(valid_depths)]
    
    if valid_depths.size == 0:
        return None
        
    # Filter outliers
    max_depth = np.max(valid_depths)
    filtered_depths = valid_depths[valid_depths <= allowed_depth * max_depth]
    
    if filtered_depths.size == 0:
        return None
        
    # Calculate average
    average_depth = np.mean(filtered_depths)
    return average_depth


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


def rectify_images(img_left, img_right):
    """
    Applies stereo rectification to image pair
    
    Args:
        img_left: Left camera image
        img_right: Right camera image
    
    Returns:
        tuple: (rectified_left, rectified_right)
    """
    img_left_rectified = cv2.remap(img_left, stereoMapL_x, stereoMapL_y, cv2.INTER_LINEAR)
    img_right_rectified = cv2.remap(img_right, stereoMapR_x, stereoMapR_y, cv2.INTER_LINEAR)
    return img_left_rectified, img_right_rectified


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
    2. Captures images from available cameras
    3. Applies image rectification
    4. Detects faces and objects in each image
    5. Calculates stereo disparity and depth for detected objects
    6. Performs face recognition on detected faces
    7. Displays combined visualization with depth information
    """
    # Stream state tracking
    stream_to_recover = False
    stream_active = False

    # Initialize camera configurations
    update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
    update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)

    # Pre-build face recognition model
    DeepFace.build_model(MODEL)

    while True:
        # Handle stream recovery if needed
        if stream_to_recover and stream_active:
            print("Stream is being recovered.")
            update_camera_config(esp32_left_config_url, JPEG_QUALITY, FRAME_SIZE)
            update_camera_config(esp32_right_config_url, JPEG_QUALITY, FRAME_SIZE)
            stream_to_recover = False
            stream_active = False

        # Fetch images from both cameras
        img_left, img_right = get_stereo_images(esp32_left_image_url, esp32_right_image_url)

        # Check if both images are missing
        if img_left is None and img_right is None:
            print("Both images are None.")
            stream_to_recover = True
            cv2.waitKey(500)
            continue
        
        # Apply rectification to available images
        if img_left is not None:
            stream_active = True
            img_left_rectified = rectify_left_image(img_left)
        if img_right is not None:
            stream_active = True
            img_right_rectified = rectify_right_image(img_right)

        # Detect faces and objects in left image if available
        if img_left is not None:
            left_face_bbox = get_face_bounding_box(img_left_rectified)
            left_object_bboxes, left_object_labels = get_object_bounding_boxes(img_left_rectified, label_filter=LABELS)
        
        # Detect faces and objects in right image if available
        if img_right is not None:
            right_face_bbox = get_face_bounding_box(img_right_rectified)
            right_object_bboxes, right_object_labels = get_object_bounding_boxes(img_right_rectified, label_filter=LABELS)

        # Handle single-camera case
        img_rectified_if_single = None
        img_face_bbox_if_single = None
        img_object_bboxes_if_single = None
        img_object_labels_if_single = None
        
        if img_left is None and img_right is not None:
            img_rectified_if_single = img_right
            img_face_bbox_if_single = right_face_bbox
            img_object_bboxes_if_single = right_object_bboxes
            img_object_labels_if_single = right_object_labels
        elif img_left is not None and img_right is None:
            img_rectified_if_single = img_left
            img_face_bbox_if_single = left_face_bbox
            img_object_bboxes_if_single = left_object_bboxes
            img_object_labels_if_single = left_object_labels

        # Process stereo case (both cameras available)
        if img_left is not None and img_right is not None:
            
            # Check if faces or objects detected in both images
            if (left_face_bbox is not None and right_face_bbox is not None) or \
                (len(left_object_bboxes) > 0 and len(right_object_bboxes) > 0):

                # Calculate disparity and 3D points for depth estimation
                disp_norm, points_3D = calculate_disparity_maps(stereo, img_left_rectified, img_right_rectified)

                # Process detected face
                if left_face_bbox is not None:
                    x, y, w, h = left_face_bbox
                    result = recognize_face(img_left_rectified)
                    if result is not None:
                        draw_boxes_and_labels(img_left_rectified, result)
                    else:
                        cv2.rectangle(img_left_rectified, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Process detected objects
                for bbox, label in zip(left_object_bboxes, left_object_labels):
                    x, y, w, h = bbox
                    
                    # Draw on disparity map
                    cv2.rectangle(disp_norm, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.putText(disp_norm, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    
                    # Draw on color image
                    cv2.rectangle(img_left_rectified, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img_left_rectified, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Calculate and display depth
                    average_object_depth = calculate_average_depth(points_3D, bbox, allowed_depth=ALLOWED_DEPTH)
                    if average_object_depth is not None:
                        cv2.putText(disp_norm, f"Depth: {average_object_depth:.2f}", (x, y + h + 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                        print(f"{label} detected. Average {label} depth: {average_object_depth:.2f}")

                # Create combined visualization
                disp_norm_color = cv2.cvtColor(disp_norm, cv2.COLOR_GRAY2BGR)
                combined = np.concatenate((disp_norm_color, img_left_rectified), axis=1)
                cv2.imshow("Disparity map", combined)
        
        # Process single-camera case
        elif img_rectified_if_single is not None:
            
            # Process detected face
            if img_face_bbox_if_single is not None:
                x, y, w, h = img_face_bbox_if_single
                result = recognize_face(img_rectified_if_single)
                if result is not None:
                    draw_boxes_and_labels(img_rectified_if_single, result)
                else:
                    cv2.rectangle(img_rectified_if_single, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Process detected objects
            for bbox, label in zip(img_object_bboxes_if_single, img_object_labels_if_single):
                x, y, w, h = bbox
                cv2.rectangle(img_rectified_if_single, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img_rectified_if_single, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Display single-camera view
            cv2.imshow("Disparity map", img_rectified_if_single)

        # Exit on 'q' key press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
    cv2.destroyAllWindows()