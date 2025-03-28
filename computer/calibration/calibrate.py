"""
Stereo Camera Calibration Script
Calibrates two ESP32-CAMs with fisheye lenses for stereo vision
Features:
- Individual camera calibration (intrinsic parameters)
- Stereo pair calibration (extrinsic parameters)
- Chessboard corner detection and visualization
- Image pair synchronization verification
- Error tracking and reporting
"""

import os
import re
import cv2
import glob
import numpy as np

# Chessboard configuration
SQUARE_SIZE = 2.45                 # Square size in centimeters
CHESSBOARD_SIZE = (9, 6)           # Inner corner dimensions (width, height)
CORNER_SUBPIX_WINDOW_SIZE = (9, 9) # Corner refinement window size

# Generate object points for chessboard corners in 3D space
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2) * SQUARE_SIZE

# Storage for calibration points
objpoints = []          # 3D points in real-world space
imgpoints_left = []     # 2D points in left image plane
imgpoints_right = []    # 2D points in right image plane


def extract_timestamp(filename):
    """
    Extracts timestamp from image filename
    
    Args:
        filename: Image filename (format: stereo_image_YYYYMMDD_HHMMSS.jpg)
    
    Returns:
        str: Timestamp or None if not found
    """
    match = re.search(r'(\d{8}_\d{6})', filename)
    return match.group(0) if match else None


def show_side_by_side(img1, img2, window_name='Side-by-side', display_time=500):
    """
    Displays two images side by side temporarily
    
    Args:
        img1: First image
        img2: Second image
        window_name: Display window title
        display_time: Display duration in milliseconds
    """
    combined_image = np.concatenate((img1, img2), axis=1)
    cv2.imshow(window_name, combined_image)
    cv2.waitKey(display_time)
    cv2.destroyAllWindows()


def save_side_by_side(img1, img2, filename, output_dir):
    """
    Saves two images concatenated side by side
    
    Args:
        img1: First image
        img2: Second image
        filename: Output filename
        output_dir: Output directory path
    """
    combined_image = np.concatenate((img1, img2), axis=1)
    cv2.imwrite(os.path.join(output_dir, filename), combined_image)


def process_image_pairs():
    """
    Processes stereo image pairs to find and validate chessboard corners
    
    Returns:
        tuple: Image size, object points, and image points for both cameras
    """
    # Load and sort images
    images_left = glob.glob('images/left_eye/*.jpg')
    images_right = glob.glob('images/right_eye/*.jpg')
    images_left.sort(key=extract_timestamp)
    images_right.sort(key=extract_timestamp)

    # Validate image counts
    assert len(images_left) == len(images_right), "Different number of images for each camera"

    # Setup output directory
    side_by_side_images_path = "images/corners_side_by_side"
    os.makedirs(side_by_side_images_path, exist_ok=True)

    # Clear previous results
    for f in glob.glob(f"{side_by_side_images_path}/*"):
        os.remove(f)

    # Corner detection parameters
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for img_left, img_right in zip(images_left, images_right):
        # Verify image pair timestamps match
        timestamp_left = extract_timestamp(img_left)
        timestamp_right = extract_timestamp(img_right)
        assert timestamp_left == timestamp_right, f"Timestamp mismatch: {img_left} and {img_right}"

        # Load and convert images
        imgL = cv2.imread(img_left)
        imgR = cv2.imread(img_right)
        grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
        grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

        # Find chessboard corners
        retL, cornersL = cv2.findChessboardCorners(grayL, CHESSBOARD_SIZE, None)
        retR, cornersR = cv2.findChessboardCorners(grayR, CHESSBOARD_SIZE, None)

        if retL and retR:
            # Refine corner positions
            cornersL = cv2.cornerSubPix(grayL, cornersL, CORNER_SUBPIX_WINDOW_SIZE, (-1, -1), criteria)
            cornersR = cv2.cornerSubPix(grayR, cornersR, CORNER_SUBPIX_WINDOW_SIZE, (-1, -1), criteria)

            # Store calibration points
            objpoints.append(objp.copy())
            imgpoints_left.append(cornersL)
            imgpoints_right.append(cornersR)

            # Visualize corners
            imgL_drawn = cv2.drawChessboardCorners(imgL.copy(), CHESSBOARD_SIZE, cornersL, retL)
            imgR_drawn = cv2.drawChessboardCorners(imgR.copy(), CHESSBOARD_SIZE, cornersR, retR)
            
            show_side_by_side(imgL_drawn, imgR_drawn, "Chessboard Corners", 500)
            save_side_by_side(imgL_drawn, imgR_drawn, f"{timestamp_left}_side_by_side.jpg", 
                            side_by_side_images_path)
        else:
            print(f"Chessboard corners not found for {img_left} and {img_right}")

    # Format data for calibration
    objpoints_reshaped = [objp.reshape(-1, 1, 3) for _ in range(len(imgpoints_left))]
    
    # Ensure image points are in the correct format
    imgpoints_left_formatted = [ip.astype(np.float32) for ip in imgpoints_left]
    imgpoints_right_formatted = [ip.astype(np.float32) for ip in imgpoints_right]
    
    # Debug info
    print("Object Points Shape and Type:", np.array(objpoints_reshaped).shape, np.array(objpoints_reshaped).dtype)
    print("Image Points Left Shape and Type:", np.array(imgpoints_left_formatted).shape, np.array(imgpoints_left_formatted).dtype)
    print("Image Points Right Shape and Type:", np.array(imgpoints_right_formatted).shape, np.array(imgpoints_right_formatted).dtype)

    return grayL.shape[::-1], objpoints_reshaped, imgpoints_left_formatted, imgpoints_right_formatted


def calibrate_cameras(img_size, objpoints, imgpoints_left, imgpoints_right):
    """
    Performs intrinsic and stereo calibration of the cameras
    
    Args:
        img_size: Image dimensions (width, height)
        objpoints: 3D calibration points (properly reshaped)
        imgpoints_left: 2D points from left camera
        imgpoints_right: 2D points from right camera
    
    Returns:
        dict: Calibration parameters and errors, or None if calibration fails
    """
    # Prepare calibration arrays
    K_left = np.zeros((3, 3))
    D_left = np.zeros((4, 1))
    K_right = np.zeros((3, 3))
    D_right = np.zeros((4, 1))

    # Set calibration flags and criteria
    flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC | cv2.fisheye.CALIB_CHECK_COND | cv2.fisheye.CALIB_FIX_SKEW
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

    calibration = {}

    # Calibrate left camera
    try:
        rms_left, K_left, D_left, rvecs_left, tvecs_left = cv2.fisheye.calibrate(
            objpoints, imgpoints_left, img_size, K_left, D_left, flags=flags, criteria=criteria)
        print(f"Left Camera Calibration RMS Error: {rms_left}")
        calibration.update({'K_left': K_left, 'D_left': D_left, 
                          'rvecs_left': rvecs_left, 'tvecs_left': tvecs_left})
    except Exception as e:
        print("Left camera calibration failed:", e)
        return None

    # Calibrate right camera
    try:
        rms_right, K_right, D_right, rvecs_right, tvecs_right = cv2.fisheye.calibrate(
            objpoints, imgpoints_right, img_size, K_right, D_right, flags=flags, criteria=criteria)
        print(f"Right Camera Calibration RMS Error: {rms_right}")
        calibration.update({'K_right': K_right, 'D_right': D_right, 
                          'rvecs_right': rvecs_right, 'tvecs_right': tvecs_right})
    except Exception as e:
        print("Right camera calibration failed:", e)
        return None

    # Perform stereo calibration
    try:
        rms_stereo, _, _, _, _, R, T, E, F = cv2.fisheye.stereoCalibrate(
            objpoints, imgpoints_left, imgpoints_right, 
            K_left, D_left, K_right, D_right, 
            img_size, flags=cv2.fisheye.CALIB_FIX_INTRINSIC, criteria=criteria)
        print(f"Stereo Calibration RMS Error: {rms_stereo}")
        calibration.update({'R': R, 'T': T, 'E': E, 'F': F})
    except Exception as e:
        print("Stereo calibration failed:", e)
        return None

    # Print camera matrices
    print("Camera Matrix Left Eye:\n", K_left)
    print("Camera Matrix Right Eye:\n", K_right)

    return calibration


def save_calibration(calibration):
    """
    Saves calibration parameters to files
    
    Args:
        calibration: Dictionary of calibration parameters
    """
    os.makedirs('parameters', exist_ok=True)
    
    # Save individual camera parameters
    for eye in ['left', 'right']:
        np.save(f'parameters/camera_matrix_{eye}_eye.npy', calibration[f'K_{eye}'])
        np.save(f'parameters/distortion_coeffs_{eye}_eye.npy', calibration[f'D_{eye}'])
        np.save(f'parameters/rotation_vec_{eye}_eye.npy', calibration[f'rvecs_{eye}'])
        np.save(f'parameters/translation_vec_{eye}_eye.npy', calibration[f'tvecs_{eye}'])
    
    # Save stereo calibration parameters
    np.save('parameters/rotation_matrix.npy', calibration['R'])
    np.save('parameters/translation_vector.npy', calibration['T'])
    np.save('parameters/essential_matrix.npy', calibration['E'])
    np.save('parameters/fundamental_matrix.npy', calibration['F'])


def main():
    """
    Main calibration process:
    1. Process image pairs and detect chessboard corners
    2. Perform camera calibrations
    3. Save calibration parameters
    """
    print("Starting camera calibration process...")
    
    # Process image pairs
    img_size, objpoints, imgpoints_left, imgpoints_right = process_image_pairs()
    
    # Perform calibration
    calibration = calibrate_cameras(img_size, objpoints, imgpoints_left, imgpoints_right)
    if calibration is None:
        print("Calibration failed")
        return
    
    # Save results
    save_calibration(calibration)
    print("Calibration completed and results saved.")


if __name__ == "__main__":
    main()