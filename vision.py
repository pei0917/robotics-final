from flask import Flask, request, jsonify
import requests
import time
import os
import cv2
from ultralytics import YOLO
from collections import Counter
import logging
import re
from collections import deque
restock_deque = deque()


def check_product(target_product):

    target_product = re.sub(r'_\d+', '', target_product).lower()
    logging.getLogger('ultralytics').setLevel(logging.ERROR)
    model = YOLO('yolov8n.pt')
    required_counts = {"vase": 1, "keyboard": 3, "bottle": 1, "cup": 1}
    max_detections = {key: 0 for key in required_counts}

    if 'cap' in locals():
        cap.release()
    cv2.destroyAllWindows()
    detection_duration = 3
    start_time = time.time()
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        exit()

    print("Starting detection. Press 'q' to quit.")
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
        annotated_frame = results[0].plot()
        y_offset = 50
        for label, count in max_detections.items():
            cv2.putText(annotated_frame, f"{label}: {count}",
                        (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            y_offset += 30
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    missing_objects = [
        obj for obj, required in required_counts.items()
        if max_detections.get(obj, 0) < required
    ]

    print("--------------------END OF DETECTION--------------------")
    print("Maximum detections:", max_detections)

    product = "None"        
    if target_product in missing_objects:
        detected_count = max_detections.get(target_product, 0)
        print(
            f"{target_product}: Detected {detected_count}, Required {required_counts[target_product]}")
    else:
        print(f"Required {target_product} met its count.")
    return product
