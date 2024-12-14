import time
import cv2
from ultralytics import YOLO
from collections import Counter
import logging
import re
from collections import deque
import threading
from queue import Queue
from queue import Empty
from threading import Lock
restock_deque = deque()

coordinate_dict = {
    'Entrance': 1,
    'Vase Area': 2,
    'Keyboard Area': 3,
    'Bottle Area': 4,
    'Cup Area': 5,
    'Stock': 6
}

class Vision():
    def __init__(self):
        self.frame_queue = Queue()
        self.frame_queue_lock = Lock()
        self.model = YOLO('yolov8n.pt')
        
    def check_product(self, target_product):

        target_product = re.sub(r'_\d+', '', target_product).lower()
        logging.getLogger('ultralytics').setLevel(logging.ERROR)
        required_counts = {"vase": 1, "keyboard": 3, "bottle": 1, "cup": 1}
        max_detections = {key: 0 for key in required_counts}

        if 'cap' in locals():
            cap.release()

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
            results = self.model(frame)
            detected_labels = [self.model.names[int(
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

            with self.frame_queue_lock:
                self.frame_queue.put(annotated_frame)

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
    
    def run(self):
        detection_duration = 1
        start_time = time.time()
        while True:
            try:

                if time.time() - start_time > detection_duration:
                    cv2.destroyAllWindows()
                with self.frame_queue_lock:
                    frame = self.frame_queue.get(timeout=0.2)
                cv2.imshow("YOLO Real-Time Detection", frame)
                start_time = time.time()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Empty:
                continue
        cv2.destroyAllWindows()