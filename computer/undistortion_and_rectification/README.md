# Notes on the `undistortion_and_rectification/` code:

## Configuration

- The script uses these paths:

```
LEFT_EYE_IMAGES_DIR = '../calibration/images/left_eye'
RIGHT_EYE_IMAGES_DIR = '../calibration/images/right_eye'
OUTPUT_DIR = './images/undistorted_and_rectified_calibration_images'
STEREO_MAPS_DIR = './stereo_maps'
```

- Calibration parameters are loaded from:

```camera_matrix_left = np.load('../calibration/parameters/camera_matrix_left_eye.npy')
dist_coeffs_left = np.load('../calibration/parameters/distortion_coeffs_left_eye.npy')
camera_matrix_right = np.load('../calibration/parameters/camera_matrix_right_eye.npy')
dist_coeffs_right = np.load('../calibration/parameters/distortion_coeffs_right_eye.npy')
R = np.load('../calibration/parameters/rotation_matrix.npy')
T = np.load('../calibration/parameters/translation_vector.npy')
```

## Process Flow

- The script performs these operations:

- Initializes stereo rectification using the fisheye camera model
- Saves the rectification maps for future use
- Processes each image pair:

  - Applies undistortion and rectification
  - Combines images side-by-side
  - Saves the resulting images

## Notes

- Uses zero disparity setting for better results with parallel cameras
- Includes commented-out code for adding horizontal lines to visualize epipolar alignment
- Rectification maps are saved separately to avoid recomputation for real-time applications
- Expects input images in JPG format from both left and right cameras
