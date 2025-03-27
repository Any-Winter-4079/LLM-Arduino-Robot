# Notes on the `depth_and_face_recognition/` code:

## Computer Setup

- Define in this line whether the robot and computer will share the phone hotspot (True) or the home WiFi (False) as the common network for communication:

```
USE_HOTSPOT = True
```

- Define in these lines the ESP32-CAMs' IPs the phone hotspot or home WiFi will assign:

```
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
```

## Database Setup

- Duplicate `face_recognition/production_database` as `depth_and_face_recognition/production_database`

## Additional Files Required

- For object detection:

  - `yolov8n.pt` file in the same folder as the script
  - `coco.names` file in the same folder as the script

- For stereo rectification:

  - Stereo rectification maps must exist in `../undistortion_and_rectification/stereo_maps/`

## Configuration

- The script can be configured through these parameters:

```
# Camera settings
JPEG_QUALITY = 12                # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution

# Object detection
ALLOWED_DEPTH = 0.875            # Maximum allowed depth percentage
LABELS = ["bottle"]              # Filter object detection to these labels

# DeepFace settings
BACKEND = "fastmtcnn"            # Face detection backend
MODEL = "VGG-Face"               # Face recognition model
DISTANCE_METRIC = "cosine"       # Similarity metric
THRESHOLD = 0.625                # Recognition threshold
```

## Functionality

- The script provides multiple capabilities that work together:

1. Face Recognition:

   - Detects faces using MediaPipe
   - Recognizes faces using DeepFace against the `production_database`
   - Draws bounding boxes and person names

2. Object Detection:

   - Detects objects using YOLOv8
   - Can filter detection to specific object classes
   - Draws bounding boxes and object labels

3. Depth Calculation:

   - Calculates disparity maps when both cameras are available
   - Computes 3D point clouds from disparity
   - Measures object depth within bounding boxes
   - Shows depth values on screen

4. Adaptive Operation:

   - Works with both cameras for full functionality
   - Falls back to single camera if one fails
   - Automatically recovers camera streams
   - Adjusts functionality based on available data

## Notes

- For optimal performance with ESP32-CAMs, use `fastmtcnn` backend and `VGG-Face` model
- Stereo parameters can be adjusted in real-time through trackbars
- Object detection can be filtered to specific labels (e.g., "bottle")
- The first model loading is slower than subsequent operations
