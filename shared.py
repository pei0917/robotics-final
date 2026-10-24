import os
import time
import threading
from collections import Counter
import logging
import re
from collections import deque
restock_deque = deque()

coordinate_dict = {
    'Entrance': 1,
    'Vase Area': 2,
    'Keyboard Area': 3,
    'Bottle Area': 4,
    'Cup Area': 5,
    'Stock': 6
}

# Webcam device index used by check_product(); override with ROBOT_CAMERA_INDEX.
CAMERA_INDEX = int(os.getenv("ROBOT_CAMERA_INDEX", "2"))

_vision_lock = threading.Lock()
_yolo_model = None

def _load_vision():
    """Lazily import the vision stack and cache the YOLO model across calls.

    cv2 / ultralytics are imported here instead of at module level so that
    ui.py, which only needs restock_deque / coordinate_dict, can import this
    module without having them installed.
    """
    global _yolo_model
    import cv2
    from ultralytics import YOLO
    with _vision_lock:
        if _yolo_model is None:
            logging.getLogger('ultralytics').setLevel(logging.ERROR)
            _yolo_model = YOLO('yolov8n.pt')
    return cv2, _yolo_model

def check_product(target_product):
    try:
        cv2, model = _load_vision()
    except ImportError as e:
        print(f"Error: vision dependencies not available ({e}).")
        return "None"

    target_product = re.sub(r'_\d+', '', target_product).lower()
    required_counts = {"vase": 1, "keyboard": 3, "bottle": 1, "cup": 1}
    max_detections = {key: 0 for key in required_counts}

    detection_duration = 3
    start_time = time.time()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: Unable to access the webcam (index {CAMERA_INDEX}).")
        return "None"

    print(f"Starting detection for {detection_duration}s.")
    while True:
        if time.time() - start_time > detection_duration:
            break
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read from the webcam.")
            break
        results = model(frame)
        detected_labels = [model.names[int(
            box.cls)] for box in results[0].boxes] if results[0].boxes else []
        label_counts = Counter(detected_labels)
        for label in required_counts.keys():
            max_detections[label] = max(
                max_detections[label], label_counts.get(label, 0))
    cap.release()
    missing_objects = [
        obj for obj, required in required_counts.items()
        if max_detections.get(obj, 0) < required
    ]

    print("--------------------END OF DETECTION--------------------")
    print("Maximum detections:", max_detections)

    if target_product in missing_objects:
        detected_count = max_detections.get(target_product, 0)
        print(
            f"{target_product}: Detected {detected_count}, Required {required_counts[target_product]}")
        return target_product
    else:
        print(f"Required {target_product} met its count.")
        return "None"
