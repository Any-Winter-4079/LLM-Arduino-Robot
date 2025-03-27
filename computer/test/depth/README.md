# Notes on the `depth/` code:

## Computer Setup

- Define in this line whether the robot and computer will share the phone hotspot (True) or the home WiFi (False) as the common network for communication (e.g., sending images):

```
USE_HOTSPOT = True
```

- Define in these lines the ESP32-CAMs' IPs the phone hotspot or home WiFi will assign:

```
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
```

- Clone the Depth Anything repository (inside the `depth` folder) and rename it to depth_anything.

  - https://github.com/LiheYoung/Depth-Anything

- Replace `run.py` and `dpt.py` (inside a second `depth_anything` folder) with the provided files.

- The structure should look like this:

```
depth
├── depth_anything
│   ├── depth_anything
│   │   ├── dpt.py
│   └── run.py
├── calculate_depth_with_depth_anything.py
```

Remember to install the Depth Anything requirements:

```
cd depth_anything
pip install -r requirements.txt
cd ..
```

## Configuration

- Camera settings can be adjusted through these parameters:

```
JPEG_QUALITY = 12                # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA"     # 640x480 resolution
```

- Timeout settings for reliable connections:

```
STREAM_TIMEOUT = 3               # seconds
CONFIG_TIMEOUT = 5               # seconds
```

## Process Flow

- The scripts support two approaches to depth perception:

  - Depth Anything (Neural Network):

    - Uses a pretrained monocular depth estimation model
    - Provides robust depth maps from single images
    - Supports different model sizes (vits, vitb, vitl)
    - Only requires one camera, though captures from both for redundancy
    - Could be calculated as soon as one frame is obtained

- Traditional Stereo Vision:

  - Uses OpenCV's StereoSGBM for disparity calculation
  - Includes real-time parameter adjustment through trackbars
  - Face detection triggers disparity map calculation
  - Requires both cameras to work properly

- Both approaches:

  - Apply stereo rectification using previously calibrated maps
  - Include automatic stream recovery if connections are lost
  - Support fallback to single camera when needed
  - Monitor and report performance metrics

## Notes

- Stereo rectification maps must exist in `../../undistortion_and_rectification/stereo_maps/`
- Camera streams will automatically recover if lost
