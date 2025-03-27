"""
Face Recognition Benchmark Tool
Tests face recognition models and detection backends on identification tasks
Features:
- Multiple recognition models (VGG-Face, Facenet, ArcFace, etc.)
- Multiple detection backends (OpenCV, MTCNN, RetinaFace, etc.)
- Performance comparison across backends
- Recognition accuracy metrics
- Processing time analysis
- Visualization of results
"""

import os
import time
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt

# Configuration
BACKENDS = [
    'opencv', 
    'ssd', 
    'mtcnn', 
    'retinaface', 
    'mediapipe',
    'yolov8',
    'yunet',
    'fastmtcnn',
]

MODELS = [
    "VGG-Face",
    "Facenet",
    "Facenet512",
    "OpenFace",
    "DeepID",
    "ArcFace"
]

DISTANCE_METRICS = ["cosine", "euclidean", "euclidean_l2"]

# Directory paths for test images and reference database
TEST_IMAGES_PATH = "1_test_images"
DATABASE_PATH = "1_database"

# Default threshold information (commented for reference)
# THRESHOLD = 1.1 # (distances < this threshold will be returned from the find function.
# In other words, set how close the match should be. Lower values risk false negatives,
# high values risk getting false positives.)
# Note different metrics (and models) require different thresholds
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

# Active testing configuration
MODEL = MODELS[5]                   # ArcFace
BACKEND = BACKENDS[7]               # fastmtcnn for plot_recognition_times()
DISTANCE_METRIC = DISTANCE_METRICS[0]  # cosine
    
def validate_recognition(prediction, test_image_file):
    """
    Validates recognition results against expected identity
    
    Args:
        prediction: Path to predicted identity from recognition
        test_image_file: Test image filename
    
    Returns:
        int: 1 if prediction is correct, 0 otherwise
    """
    # Extract predicted name from the identity path
    predicted_name = prediction.split('/')[-1]
    predicted_name = "_".join(predicted_name.split('_')[:-1])
    predicted_name = predicted_name.lower()
    print(f"Predicted name: {predicted_name}")

    # Extract actual name from test image filename
    actual_name = "_".join(test_image_file.split('_')[:-1])
    actual_name = actual_name.lower()
    print(f"Actual name: {actual_name}")
    
    # Return 1 for match, 0 for mismatch
    return 1 if predicted_name == actual_name else 0


def recognize_face(test_image_path, backend=BACKEND):
    """
    Recognizes a face in an image using DeepFace
    
    Args:
        test_image_path: Path to image for recognition
        backend: Face detection backend to use
    
    Returns:
        DataFrame row: Top prediction for recognized face or None
    """
    try:
        dfs = DeepFace.find(
            img_path=test_image_path,
            db_path=DATABASE_PATH,
            model_name=MODEL,
            detector_backend=backend,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=False,
            # threshold=THRESHOLD
        )
        # dfs is a list of dataframes, one dataframe per face recognized
        # 1_test_images in this basic version are not meant for >1 face
        face = dfs[0]
        # Once we have the face, we return its top prediction
        return face.iloc[0] if len(face) > 0 else None
    except Exception as e:
        print(f"\nAn error occurred recognizing {test_image_path} with model {MODEL} and backend {backend}: {e}\n")


def plot_recognition_times():
    """
    Plots recognition processing time for each test image
    
    Builds the model first for faster performance, and measures the time
    taken to recognize faces in each test image using the specified backend.
    """
    # Build model for faster performance, but at the same time, building the model
    # is what (I think) takes the most time, so if we looped here for >1 backend,
    # the first backend would seemingly have a spike in the first image,
    # while the other backends would not (because they would take advantage of the
    # already built model). And given the purpose is to see the spike, we leave it
    # this way.
    DeepFace.build_model(MODEL)
    
    times = []
    test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
    
    # Process each test image and measure recognition time
    for test_image_file in test_image_files:
        test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
        start_time = time.time()
        _ = recognize_face(test_image_path)
        end_time = time.time()
        times.append(end_time - start_time)
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(test_image_files)), times, edgecolor='black', color='#4BA081',)
    plt.xlabel('Test Image')
    plt.ylabel('Recognition time (s)')
    plt.title(f'Recognition times for {BACKEND} and {MODEL}')
    plt.xticks(range(len(test_image_files)), labels=[f.split('.')[0] for f in test_image_files], rotation=90)
    plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_backend_comparison(results, test_image_files):
    """
    Creates visualization comparing performance across backends
    
    Args:
        results: Dictionary containing performance data for each backend
        test_image_files: List of test image files
    """
    backends = list(results.keys())
    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_predictions = [results[backend]["correct_predictions"] for backend in backends]

    # Create figure with primary y-axis
    fig, ax1 = plt.subplots()

    # Plot correct recognitions bars
    color = '#4BA081'
    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Correct recognitions', color='black')
    bars = ax1.bar(backends, correct_predictions, color=color, edgecolor='black', label='Correct recognitions')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xticks(range(len(backends)))
    ax1.set_xticklabels(backends, rotation=45, ha="right")
    ax1.set_ylim(0, len(test_image_files))

    # Add data labels to bars
    for bar in bars:
        height = bar.get_height()
        ax1.annotate('{}'.format(height),
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')

    # Add secondary y-axis for timing information
    ax2 = ax1.twinx()
    color = '#387761'
    ax2.set_ylabel('Average time (s)', color='black')
    ax2.plot(backends, average_times, color=color, marker='o', linestyle='-', linewidth=2, markersize=5)
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

    fig.tight_layout()
    plt.title(f'Correct predictions (bars) and average time (lines) for {MODEL} and {DISTANCE_METRIC}.')
    plt.show()


def test_backends():
    """
    Evaluates all detection backends for face recognition performance
    
    Tests each backend with the selected model and distance metric against
    the test images, and compares:
    - Recognition accuracy (correct predictions)
    - Processing speed (average time)
    """
    results = {}
    for backend in BACKENDS:
        # Build model for faster performance
        DeepFace.build_model(MODEL)

        predictions = {
            "correct_predictions": 0,
            "times": []
        }
        
        # Process each test image with current backend
        test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
        for test_image_file in test_image_files:
            test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
            
            # Measure recognition time
            start_time = time.time()
            result = recognize_face(test_image_path, backend=backend)
            end_time = time.time()
            
            # Update results
            predictions["correct_predictions"] += validate_recognition(result['identity'], test_image_file) if result is not None else 0
            predictions["times"].append(end_time - start_time)
        
        results[backend] = predictions

    # Visualize the results
    plot_backend_comparison(results, test_image_files)

    # Print summary results
    backends = list(results.keys())
    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_predictions = [results[backend]["correct_predictions"] for backend in backends]
    
    for backend in BACKENDS:
        print(f"Backend: {backend}")
        print(f"\tAverage time: {average_times[backends.index(backend)]:.4f} seconds")
        print(f"\tCorrect predictions: {correct_predictions[backends.index(backend)]} out of {len(test_image_files)}\n")


if __name__ == "__main__":
    test_backends()
    #plot_recognition_times()  # Run without running test_backends() to account for the model building time