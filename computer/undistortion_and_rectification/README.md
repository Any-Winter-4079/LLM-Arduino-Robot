# Notes on the `undistortion_and_rectification/` code:

## Stereo Image Processing System

This script performs undistortion and rectification of calibrated stereo camera images to prepare them for depth perception.

## Features

- Fisheye lens distortion correction
- Stereo image rectification for epipolar alignment
- Rectification map generation and storage
- Batch processing of calibration images
- Side-by-side visualization of rectified pairs

## Directory Structure

- `./images/undistorted_and_rectified_calibration_images/`: Output directory for processed image pairs
- `./stereo_maps/`: Storage location for generated rectification maps

## Dependencies

The script requires:

- OpenCV (cv2)
- NumPy
- Previously generated calibration parameters from `calibration/parameters/`

## Process Flow

1. **Load Calibration Parameters**:

- Camera matrices
- Distortion coefficients
- Rotation matrix
- Translation vector

2. **Initialize Rectification**:

- Calculate rectification transforms
- Generate undistortion maps for both cameras

3. **Process Images**:

- Apply undistortion and rectification to all image pairs
- Create side-by-side visualizations
- Save processed images and rectification maps

## Usage

Simply run the script:
