# Notes on the `face_recognition/` code:

## Computer Setup

- Define in this line whether the robot and computer will share the phone hotspot (True) or the home WiFi (False) as the common network for communication:

```
USE_HOTSPOT = False
```

- Define in these lines the ESP32-CAMs' IPs the phone hotspot or home WiFi will assign:

```
RIGHT_EYE_IP = "172.20.10.10" if USE_HOTSPOT else "192.168.1.180"
LEFT_EYE_IP = "172.20.10.11" if USE_HOTSPOT else "192.168.1.181"
```

## Dataset Recommendations

### For Known Faces Benchmark

- Consider using the [Labelled Faces in the Wild (LFW) Dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset?resource=download)
- For testing with known faces:

  - Take all people with names starting with 'A' (~432 people with ~1054 images)
  - Move the last image of every person with 4+ images (up to 30 people) to a `1_test_images` folder
  - Remove these test images from the `1_database` folder

```
1_database/
├── Aaron_Eckhart/
│   ├── Aaron_Eckhart_0001.jpg
│   ├── Aaron_Eckhart_0002.jpg
│   ├── Aaron_Eckhart_0003.jpg
├── Aaron_Guiel/
│   ├── Aaron_Guiel_0001.jpg
...

1_test_images/
├── Aaron_Peirsol_0004.jpg
├── Aaron_Eckhart_0004.jpg
...
```

### For Known and Unknown Faces Benchmark

- Duplicate `1_database` to create `2_database`
- Add specific known people (e.g., celebrities like Tom_Cruise, Salma_Hayek, Valentino_Rossi, and Arnold_Schwarzenegger)
- Include 3-4 images per person in different poses (front_close, front_far, etc.)
- All images should be resized to the same dimensions (e.g., 250x250 pixels)
- Create a `2_test_images` folder with:

  - 4 known people (4 images each)
  - 4 unknown people (4 images each)
  - 16 images without faces

```
2_database/
├── Aaron_Eckhart/
│   ├── Aaron_Eckhart_0001.jpg
...
├── Tom_Cruise/
│   ├── Tom_Cruise_0001.jpg
...

2_test_images/
├── Salma_Hayek_front_close_known_0001.jpg
├── Salma_Hayek_front_far_known_0002.jpg
├── Salma_Hayek_side_close_known_0003.jpg
├── Salma_Hayek_side_far_known_0004.jpg
├── Curry_front_close_unknown_0001.jpg
├── Curry_front_far_unknown_0002.jpg
├── Curry_side_close_unknown_0003.jpg
├── Curry_side_far_unknown_0004.jpg
├── unknown_0001.jpg
...
```

### For Production

- Create a `production_database` folder with images from people you want to recognize
- Include multiple images of each person (recommended 10-15 per person)
- All production_database images are 512x512, although frames come at 640x480
- Include multiple angles for each person: front close, front far, side close, side far

## Configuration

- The scripts can be configured through these parameters:

```
# Camera settings

JPEG_QUALITY = 12 # 0-63 lower means higher quality
FRAME_SIZE = "FRAMESIZE_VGA" # 640x480 resolution

# DeepFace settings

BACKEND = "fastmtcnn" # Face detection backend
MODEL = "VGG-Face" # Face recognition model
DISTANCE_METRIC = "cosine" # Similarity metric
THRESHOLD = 0.625 # Recognition threshold
```

- Different models and metrics require different thresholds:

```
| Model       | Cosine | Euclidean | Euclidean L2 |
|-------------|--------|-----------|--------------|
| VGG-Face    | 0.68   | 1.17      | 1.17         |
| Facenet     | 0.40   | 10        | 0.80         |
| Facenet512  | 0.30   | 23.56     | 1.04         |
| ArcFace     | 0.68   | 4.15      | 1.13         |
| Dlib        | 0.07   | 0.6       | 0.4          |
| SFace       | 0.593  | 10.734    | 1.055        |
| OpenFace    | 0.10   | 0.55      | 0.55         |
| DeepFace    | 0.23   | 64        | 0.64         |
| DeepID      | 0.015  | 45        | 0.17         |
```

## Functions

1. `benchmark_face_recognition_with_known_faces.py`:

- Tests face recognition with known faces only
- Uses `1_database` and `1_test_images` folders
- Compares different backends and models
- Plots recognition times and accuracy

2. `benchmark_face_recognition_with_unknown_and_no_faces.py`:

- Tests face recognition with known, unknown, and no faces
- Uses `2_database` and `2_test_images` folders
- Analyzes performance by image type (front_close, front_far, etc.)
- Plots both correct identifications and non-identifications
- Shows a second plot with performance per image type after closing the first plot

3. `run_face_recognition.py`:

- Real-time face recognition with ESP32-CAMs
- Uses `production_database` folder
- Draws boxes and labels around recognized faces
- Handles camera configuration and stream recovery

## Notes

- Stereo rectification maps must exist in `../undistortion_and_rectification/stereo_maps/`
- For optimal performance with ESP32-CAMs, use `fastmtcnn` backend and `VGG-Face` model
- Lower threshold values risk no matches, while higher values risk false positives
- The production script will work with either one or both cameras
- The first model loading is slower than subsequent operations
- `test_image_path` can be a numpy array in DeepFace. So we don't need to save the image to disk
