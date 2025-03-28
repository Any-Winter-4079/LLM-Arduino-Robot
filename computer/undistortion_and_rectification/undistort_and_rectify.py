"""
Stereo Image Undistortion and Rectification Script
Processes calibrated stereo camera images for depth perception
Features:
- Fisheye lens distortion correction
- Stereo image rectification for epipolar alignment
- Rectification map generation and storage
- Batch processing of calibration images
- Side-by-side visualization of rectified pairs
"""

import os
import cv2
import glob
import numpy as np

# Configuration paths
LEFT_EYE_IMAGES_DIR = '../calibration/images/left_eye'                  # Source directory for left camera images
RIGHT_EYE_IMAGES_DIR = '../calibration/images/right_eye'                # Source directory for right camera images
OUTPUT_DIR = './images/undistorted_and_rectified_calibration_images'    # Output directory for processed images
STEREO_MAPS_DIR = './stereo_maps'                                       # Directory to save rectification maps

# Load calibration parameters from previous calibration step
camera_matrix_left = np.load('../calibration/parameters/camera_matrix_left_eye.npy')
dist_coeffs_left = np.load('../calibration/parameters/distortion_coeffs_left_eye.npy')
camera_matrix_right = np.load('../calibration/parameters/camera_matrix_right_eye.npy')
dist_coeffs_right = np.load('../calibration/parameters/distortion_coeffs_right_eye.npy')
R = np.load('../calibration/parameters/rotation_matrix.npy')
T = np.load('../calibration/parameters/translation_vector.npy')


def initialize_stereo_rectification(
    image_size,
    camera_matrix_left,
    dist_coeffs_left,
    camera_matrix_right,
    dist_coeffs_right,
    R,
    T
):
    """
    Performs stereo rectification and initializes rectification maps
    
    Args:
        image_size: Dimensions of input images (width, height)
        camera_matrix_left: Intrinsic matrix for left camera
        dist_coeffs_left: Distortion coefficients for left camera
        camera_matrix_right: Intrinsic matrix for right camera
        dist_coeffs_right: Distortion coefficients for right camera
        R: Rotation matrix between cameras
        T: Translation vector between cameras
    
    Returns:
        tuple: Left and right stereo rectification maps and Q matrix
               for 3D reconstruction
    """
    # Use zero disparity setting for better results with parallel cameras
    flags = cv2.CALIB_ZERO_DISPARITY
    
    # Calculate rectification transforms
    R1, R2, P1, P2, Q = cv2.fisheye.stereoRectify(
        camera_matrix_left, dist_coeffs_left,
        camera_matrix_right, dist_coeffs_right,
        image_size, R, T, flags=flags
    )
    
    # Initialize undistortion and rectification maps for both cameras
    stereoMapL = cv2.fisheye.initUndistortRectifyMap(
        camera_matrix_left, dist_coeffs_left,
        R1, P1, image_size, cv2.CV_16SC2
    )
    stereoMapR = cv2.fisheye.initUndistortRectifyMap(
        camera_matrix_right, dist_coeffs_right,
        R2, P2, image_size, cv2.CV_16SC2
    )
    
    return stereoMapL, stereoMapR, Q


def save_stereo_maps(
    stereoMapL,
    stereoMapR,
    Q,
    directory=STEREO_MAPS_DIR
):
    """
    Saves stereo rectification maps for future reuse
    
    Args:
        stereoMapL: Left camera undistortion and rectification maps (x,y)
        stereoMapR: Right camera undistortion and rectification maps (x,y)
        Q: Disparity-to-depth mapping matrix
        directory: Output directory path
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Save individual map components
    np.save(os.path.join(directory, 'stereoMapL_x.npy'), stereoMapL[0])
    np.save(os.path.join(directory, 'stereoMapL_y.npy'), stereoMapL[1])
    np.save(os.path.join(directory, 'stereoMapR_x.npy'), stereoMapR[0])
    np.save(os.path.join(directory, 'stereoMapR_y.npy'), stereoMapR[1])
    np.save(os.path.join(directory, 'Q.npy'), Q)


def process_images(
    left_images_dir,
    right_images_dir,
    output_dir
):
    """
    Processes image pairs with undistortion and rectification
    
    Args:
        left_images_dir: Directory containing left camera images
        right_images_dir: Directory containing right camera images
        output_dir: Directory to save processed image pairs
    """
    # Find and sort all input images
    left_images = sorted(glob.glob(os.path.join(left_images_dir, '*.jpg')))
    right_images = sorted(glob.glob(os.path.join(right_images_dir, '*.jpg')))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get image size from first image (all should be the same size)
    first_left_image = cv2.imread(left_images[0])
    image_size = first_left_image.shape[1], first_left_image.shape[0]
    
    # Initialize rectification maps
    stereoMapL, stereoMapR, Q = initialize_stereo_rectification(
        image_size, camera_matrix_left, dist_coeffs_left,
        camera_matrix_right, dist_coeffs_right, R, T
    )

    # Save maps for future use (avoids recomputation for real-time applications)
    save_stereo_maps(stereoMapL, stereoMapR, Q)

    # Process each image pair
    for left_img_path, right_img_path in zip(left_images, right_images):
        # Load images
        left_img = cv2.imread(left_img_path)
        right_img = cv2.imread(right_img_path)

        # Apply undistortion and rectification
        left_img_rectified = cv2.remap(left_img, stereoMapL[0], stereoMapL[1], cv2.INTER_LINEAR)
        right_img_rectified = cv2.remap(right_img, stereoMapR[0], stereoMapR[1], cv2.INTER_LINEAR)

        # Combine images side-by-side for visualization
        combined = np.concatenate((left_img_rectified, right_img_rectified), axis=1)
        
        # Add horizontal lines to visualize epipolar alignment (optional)
        # height, width = combined.shape[:2]
        # for line in range(0, height, 50):  # Add line every 50 pixels
        #     cv2.line(combined, (0, line), (width, line), (0, 255, 0), 1)
            
        # Save the combined rectified image
        output_path = os.path.join(output_dir, os.path.basename(left_img_path))
        cv2.imwrite(output_path, combined)

        print(f"Processed and saved {left_img_path} and {right_img_path}")


def main():
    """
    Main execution function:
    1. Loads calibration parameters
    2. Processes image pairs for undistortion and rectification
    3. Saves stereo maps for future use
    """
    print("Starting stereo image undistortion and rectification...")
    process_images(LEFT_EYE_IMAGES_DIR, RIGHT_EYE_IMAGES_DIR, OUTPUT_DIR)
    print(f"Process complete. Rectified images saved to {OUTPUT_DIR}")
    print(f"Stereo rectification maps saved to {STEREO_MAPS_DIR}")


if __name__ == "__main__":
    main()