import os
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

class ModelHandler:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'yolov8n.pt')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        print(f"Loading YOLO model from {model_path}")
        self.model = YOLO(model_path)
        print("YOLO model loaded successfully")
    
    def detect(self, image_path: str, conf_threshold: float = 0.25):
        """
        Run YOLO detection on an image
        Returns list of detections with bounding boxes and class IDs
        """
        try:
            # Run inference
            results = self.model(image_path, conf=conf_threshold)
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    conf = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detection = {
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': conf,
                        'class': class_id,
                        'class_name': self.get_class_name(class_id)
                    }
                    
                    detections.append(detection)
            
            return detections
        
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def get_class_name(self, class_id: int) -> str:
        """Map class ID to class name"""
        class_names = {
            0: 'brand name',
            1: 'dosage',
            2: 'generic name'
        }
        return class_names.get(class_id, 'unknown')
    
    def visualize_detections(self, image_path: str, detections: list, output_path: str = None):
        """
        Draw bounding boxes on image
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            
            # Colors for different classes (BGR format)
            colors = {
                0: (255, 0, 0),    # Blue for brand name
                1: (0, 255, 0),    # Green for dosage
                2: (0, 0, 255)     # Red for generic name
            }
            
            for detection in detections:
                bbox = detection['bbox']
                class_id = detection['class']
                conf = detection['confidence']
                class_name = detection['class_name']
                
                x1, y1, x2, y2 = [int(coord) for coord in bbox]
                
                # Draw rectangle
                color = colors.get(class_id, (255, 255, 255))
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, color, 2)
            
            # Save or return
            if output_path:
                cv2.imwrite(output_path, img)
            
            return img
        
        except Exception as e:
            print(f"Visualization error: {e}")
            return None
