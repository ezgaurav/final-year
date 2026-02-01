import easyocr
import cv2
import numpy as np
from PIL import Image

class OCRHandler:
    def __init__(self):
        # Initialize EasyOCR reader for English
        self.reader = easyocr.Reader(['en'], gpu=False)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract all text from image using EasyOCR"""
        try:
            result = self.reader.readtext(image_path)
            # Combine all detected text
            text = ' '.join([detection[1] for detection in result])
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_text_from_bbox(self, image, bbox: list) -> str:
        """
        Extract text from a specific bounding box region
        bbox: [x1, y1, x2, y2] coordinates
        """
        try:
            # If image is a path, load it
            if isinstance(image, str):
                img = cv2.imread(image)
            elif isinstance(image, Image.Image):
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                img = image
            
            # Extract region of interest
            x1, y1, x2, y2 = [int(coord) for coord in bbox]
            roi = img[y1:y2, x1:x2]
            
            # Convert to PIL Image for EasyOCR
            roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            
            # Perform OCR on the region
            result = self.reader.readtext(np.array(roi_pil))
            
            # Combine all detected text
            text = ' '.join([detection[1] for detection in result])
            return text.strip()
        except Exception as e:
            print(f"OCR Bbox Error: {e}")
            return ""
    
    def extract_text_from_detections(self, image, detections: list) -> dict:
        """
        Extract text from YOLO detections
        detections: list of dicts with 'bbox' and 'class' keys
        Returns: dict with brand_name, dosage, generic_name
        """
        result = {
            'brand_name': '',
            'dosage': '',
            'generic_name': ''
        }
        
        class_mapping = {
            0: 'brand_name',
            1: 'dosage',
            2: 'generic_name'
        }
        
        for detection in detections:
            bbox = detection['bbox']
            class_id = detection['class']
            
            # Extract text from this bounding box
            text = self.extract_text_from_bbox(image, bbox)
            
            # Map to the correct field
            if class_id in class_mapping:
                field = class_mapping[class_id]
                # Append if there's already text (multiple detections of same class)
                if result[field]:
                    result[field] += ' ' + text
                else:
                    result[field] = text
        
        return result
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
