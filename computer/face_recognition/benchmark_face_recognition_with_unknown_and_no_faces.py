"""
Face Recognition Evaluation Framework
Tests different facial recognition models and detection backends
Features:
- Multiple recognition models (VGG-Face, Facenet, ArcFace, etc.)
- Multiple detection backends (OpenCV, MTCNN, RetinaFace, etc.)
- Performance evaluation metrics (speed, accuracy)
- Support for identification type analysis (front/side, close/far)
- Visualization of recognition performance
- Unknown subject detection validation
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
TEST_IMAGES_PATH = "2_test_images"  # make sure to create this folder and place some images there
DATABASE_PATH = "2_database"        # make sure to create this folder and place some images there

# Default threshold information (commented for reference)
# THRESHOLD = 0.5 # (distances < this threshold will be returned from the find function.
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
MODEL = MODELS[0]                   # VGG-Face as default
BACKEND = BACKENDS[7]               # fastmtcnn for plot_recognition_times()
DISTANCE_METRIC = DISTANCE_METRICS[0]  # cosine

def validate_recognition(prediction, test_image_file):
    """
    Validates recognition results against expected identity
    
    Args:
        prediction: Recognition result from DeepFace
        test_image_file: Path to test image being evaluated
    
    Returns:
        tuple: (correct identification count, correct non-identification count, identification types counts)
    """
    correct_identification = 0
    correct_non_identification = 0
    identification_types = {
        'front_close': 0,
        'front_far': 0,
        'side_close': 0,
        'side_far': 0,
    }

    # Extract actual identity from filename using naming convention
    actual_name_parts = test_image_file.split('/')[-1].split('_')
    actual_is_unknown = "unknown" in test_image_file
    identification_type = "_".join(actual_name_parts[-4:-2]) if len(actual_name_parts) > 4 else None

    # Determine actual identity from filename
    if actual_is_unknown:
        actual_name = "unknown"
    else:
        actual_name = '_'.join(actual_name_parts[:-4]).lower()

    print(f"Actual name: {actual_name}")

    # Compare predicted identity with actual identity
    if not prediction:
        print("Predicted name: unknown")
        if actual_is_unknown:
            correct_non_identification = 1
    elif prediction:
        top_prediction = prediction[0]
        identity = top_prediction["identity"]
        predicted_name = "_".join(identity.split('/')[-1].split('_')[:-1]).lower()
        print(f"Predicted name: {predicted_name}")

        if predicted_name == actual_name:
            correct_identification = 1
            identification_types[identification_type] += 1

    return correct_identification, correct_non_identification, identification_types


def get_top_predictions(dfs_list):
    """
    Extracts top predictions from recognition results
    
    Args:
        dfs_list: List of dataframes containing recognition results
    
    Returns:
        list: Top prediction for each detected face
    """
    # The list can have more than one dataframe if there are multiple faces.
    # One dataframe per face.
    # Each dataframe has one or more rows, from most likely to least likely
    # while meeting the threshold.
    top_predictions = []
    if dfs_list is not None:
        for df in dfs_list:
            if len(df) > 0:
                top_prediction = df.iloc[0]
                top_predictions.append(top_prediction)
    return top_predictions


def recognize_face(test_image_path, backend=BACKEND):
    """
    Recognizes faces in an image using DeepFace
    
    Args:
        test_image_path: Path to image for recognition
        backend: Face detection backend to use
    
    Returns:
        list: Top predictions for each detected face
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
        top_predictions = get_top_predictions(dfs)
        return top_predictions  # return top prediction for each face in the image
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
    # already built model). But given the purpose is to see the spike,
    # we leave it this way.
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
    plt.xlabel('Test image')
    plt.ylabel('Recognition time (s)')
    plt.title(f'Recognition times for {BACKEND} and {MODEL}')
    plt.xticks(range(len(test_image_files)), labels=[f.split('.')[0] for f in test_image_files], rotation=90)
    plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def test_backends():
    """
    Evaluates all detection backends for face recognition performance
    
    Tests each backend with the selected model and distance metric against
    the test images, and visualizes the results in terms of:
    - Recognition accuracy
    - Processing speed
    - Performance across different image types
    """
    results = {}
    for backend in BACKENDS:
        # Build model for faster performance
        DeepFace.build_model(MODEL)

        predictions = {
            "correct_identifications": 0,
            "correct_non_identifications": 0,
            "identification_types": {
                'front_close': 0,
                'front_far': 0,
                'side_close': 0,
                'side_far': 0,
            },
            "times": []
        }
        
        # Process each test image with current backend
        test_image_files = sorted([f for f in os.listdir(TEST_IMAGES_PATH) if os.path.isfile(os.path.join(TEST_IMAGES_PATH, f))])
        for test_image_file in test_image_files:
            test_image_path = os.path.join(TEST_IMAGES_PATH, test_image_file)
            start_time = time.time()
            result = recognize_face(test_image_path, backend=backend)
            end_time = time.time()
            
            # Validate recognition results
            correct_identification, correct_non_identification, identification_types = validate_recognition(result, test_image_file)
            predictions["correct_identifications"] += correct_identification
            predictions["correct_non_identifications"] += correct_non_identification
            for id_type in identification_types:
                predictions["identification_types"][id_type] += identification_types[id_type]
            predictions["times"].append(end_time - start_time)
        results[backend] = predictions

    # Prepare data for visualization
    backends = list(results.keys())
    average_times = [np.mean(results[backend]["times"]) for backend in backends]
    correct_identifications = [results[backend]["correct_identifications"] for backend in backends]
    correct_non_identifications = [results[backend]["correct_non_identifications"] for backend in backends]

    # Create figure for accuracy and timing visualization
    fig, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    index = np.arange(len(backends))
    rects1 = ax1.bar(index - bar_width/2, correct_identifications, bar_width, label='Correct identifications', color='#4BA081', edgecolor='black')
    rects2 = ax1.bar(index + bar_width/2, correct_non_identifications, bar_width, label='Correct non-identifications', color='#388872', edgecolor='black')

    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Number of correct predictions', color='black')
    ax1.set_title(f'Recognition performance for {MODEL} and {DISTANCE_METRIC}')
    ax1.set_xticks(index)
    ax1.set_xticklabels(backends, rotation=45, ha="right")
    ax1.legend()

    # Add data labels to bars
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax1.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Add secondary y-axis for timing information
    ax2 = ax1.twinx()  
    ax2.set_ylabel('Average time (s)', color='black')
    ax2.plot(backends, average_times, color='#387761', marker='o', linestyle='-', linewidth=2, markersize=5, label='Average time')
    ax2.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.legend(loc='upper center')

    fig.tight_layout()
    plt.show()

    # Create visualization for identification types
    n_backends = len(results)
    n_types = 4
    bar_width = 0.15
    spacing = 0.05

    backends = list(results.keys())
    id_types = ['front_close', 'front_far', 'side_close', 'side_far']
    data = np.array([[results[backend]["identification_types"][id_type] for id_type in id_types] for backend in backends])

    index = np.arange(n_backends) * (n_types * bar_width + spacing)

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#4BA081', '#388872', '#83A598', '#B8B8B8']

    # Create grouped bars for each identification type
    for i, id_type in enumerate(id_types):
        bars = ax.bar(index + i * bar_width, data[:, i], bar_width, label=id_type, color=colors[i], edgecolor='black')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.set_xlabel('Backends')
    ax.set_ylabel('Counts')
    ax.set_title(f'Counts per image type for {MODEL} and {DISTANCE_METRIC}')
    ax.set_xticks(index + bar_width * (n_types - 1) / 2)
    ax.set_xticklabels(backends, rotation=45)
    ax.legend(title="Identification types")

    ax.set_xlim(-bar_width, max(index) + bar_width * n_types + spacing)

    plt.tight_layout()
    plt.show()

    # Print summary results
    for backend in backends:
        print(f"Backend: {backend}")
        print(f"\tAverage time: {average_times[backends.index(backend)]:.4f} seconds")
        print(f"\tCorrect identifications: {correct_identifications[backends.index(backend)]}")
        print(f"\tCorrect non-identifications: {correct_non_identifications[backends.index(backend)]}")
        print(f"\tIdentification types: {results[backend]['identification_types']}\n")


if __name__ == "__main__":
    test_backends()
    #plot_recognition_times()  # Run without running test_backends() to account for the model building time