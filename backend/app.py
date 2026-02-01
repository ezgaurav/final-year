from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from typing import Optional
import base64

from model_handler import ModelHandler
from database_handler import DatabaseHandler
from ocr_handler import OCRHandler
from translator import NepaliTranslator

# Initialize FastAPI app
app = FastAPI(title="Medicine Detection API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
try:
    model_handler = ModelHandler()
    db_handler = DatabaseHandler()
    ocr_handler = OCRHandler()
    translator = NepaliTranslator()
    print("All handlers initialized successfully")
except Exception as e:
    print(f"Error initializing handlers: {e}")
    model_handler = None
    db_handler = None
    ocr_handler = None
    translator = None

# Create temp directory for uploads
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Medicine Detection API is running",
        "endpoints": [
            "/api/detect - POST: Upload image for detection",
            "/api/search - GET: Search medicine by name",
            "/api/medicine/{name} - GET: Get medicine details",
            "/api/translate - POST: Translate text to Nepali"
        ]
    }

@app.post("/api/detect")
async def detect_medicine(file: UploadFile = File(...)):
    """
    Upload an image and detect medicine information
    Returns detected text, medicine info, and Nepali translations
    """
    if not model_handler or not db_handler or not ocr_handler or not translator:
        raise HTTPException(status_code=500, detail="Handlers not initialized")
    
    # Save uploaded file
    file_path = TEMP_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
    
    try:
        # Run YOLO detection
        detections = model_handler.detect(str(file_path), conf_threshold=0.25)
        
        if not detections:
            # Fallback: Use EasyOCR on full image
            full_text = ocr_handler.extract_text_from_image(str(file_path))
            
            # Try to search database with OCR text
            search_results = db_handler.search_medicine(full_text)
            
            if search_results:
                medicine_data = search_results[0]['data']
                translated_data = translator.translate_medicine_data(medicine_data)
                
                return JSONResponse({
                    "success": True,
                    "method": "fallback_ocr",
                    "detected_text": full_text,
                    "medicine_info": translated_data,
                    "message": "Detection failed, used OCR fallback"
                })
            else:
                return JSONResponse({
                    "success": False,
                    "message": "No medicine detected. Please try a clearer image or use search.",
                    "detected_text": full_text
                })
        
        # Extract text from detected bounding boxes
        detected_text = ocr_handler.extract_text_from_detections(str(file_path), detections)
        
        # Search medicine in database
        medicine_info = db_handler.get_medicine_info(detected_text)
        
        if medicine_info:
            # Translate to Nepali
            translated_data = translator.translate_medicine_data(medicine_info)
            
            return JSONResponse({
                "success": True,
                "detections": detections,
                "detected_text": detected_text,
                "medicine_info": translated_data
            })
        else:
            # Try fallback search with all detected text combined
            all_text = ' '.join(detected_text.values())
            search_results = db_handler.search_medicine(all_text)
            
            if search_results:
                medicine_data = search_results[0]['data']
                translated_data = translator.translate_medicine_data(medicine_data)
                
                return JSONResponse({
                    "success": True,
                    "method": "fuzzy_search",
                    "detections": detections,
                    "detected_text": detected_text,
                    "medicine_info": translated_data,
                    "message": "Found using fuzzy matching"
                })
            else:
                return JSONResponse({
                    "success": False,
                    "detections": detections,
                    "detected_text": detected_text,
                    "message": "Medicine not found in database. Try searching manually."
                })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

@app.post("/api/camera")
async def process_camera_image(file: UploadFile = File(...)):
    """
    Process image from camera capture
    Same as detect endpoint but optimized for camera input
    """
    return await detect_medicine(file)

@app.get("/api/search")
async def search_medicine(q: str = Query(..., description="Search query")):
    """
    Search for medicines by name
    Returns list of matching medicines with translations
    """
    if not db_handler or not translator:
        raise HTTPException(status_code=500, detail="Handlers not initialized")
    
    try:
        results = db_handler.search_medicine(q)
        
        if not results:
            return JSONResponse({
                "success": False,
                "message": "No medicines found",
                "results": []
            })
        
        # Translate top results
        translated_results = []
        for result in results[:5]:  # Limit to top 5 for performance
            medicine_data = result['data']
            translated = translator.translate_medicine_data(medicine_data)
            translated['match_score'] = result['match_score']
            translated_results.append(translated)
        
        return JSONResponse({
            "success": True,
            "results": translated_results
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/medicine/{name}")
async def get_medicine_details(name: str):
    """
    Get detailed information about a specific medicine
    """
    if not db_handler or not translator:
        raise HTTPException(status_code=500, detail="Handlers not initialized")
    
    try:
        medicine_data = db_handler.get_medicine_by_name(name)
        
        if not medicine_data:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        # Translate to Nepali
        translated_data = translator.translate_medicine_data(medicine_data)
        
        return JSONResponse({
            "success": True,
            "medicine": translated_data
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/translate")
async def translate_text(data: dict):
    """
    Translate text to Nepali
    Request body: {"text": "text to translate"}
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    text = data.get('text', '')
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        translated = translator.translate_to_nepali(text)
        return JSONResponse({
            "success": True,
            "original": text,
            "translated": translated
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@app.get("/api/medicines/list")
async def list_all_medicines():
    """
    Get list of all medicine names (for autocomplete)
    """
    if not db_handler:
        raise HTTPException(status_code=500, detail="Database handler not initialized")
    
    try:
        medicines = db_handler.get_all_medicine_names()
        return JSONResponse({
            "success": True,
            "count": len(medicines),
            "medicines": medicines[:100]  # Limit for performance
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Demo endpoint with hardcoded Paracetamol
@app.get("/api/demo/paracetamol")
async def demo_paracetamol():
    """
    Demo endpoint with Paracetamol data
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    demo_data = {
        "Medicine_name": "Paracetamol 500mg Tablet",
        "Uses": "Treatment of Fever, Pain relief",
        "Side_effects": [
            "Nausea",
            "Vomiting",
            "Stomach pain",
            "Dark urine",
            "Fatigue"
        ]
    }
    
    try:
        translated_data = translator.translate_medicine_data(demo_data)
        return JSONResponse({
            "success": True,
            "medicine": translated_data,
            "note": "This is demo data"
        })
    except Exception as e:
        return JSONResponse({
            "success": True,
            "medicine": {
                **demo_data,
                "Medicine_name_nepali": "पारासिटामोल ५००mg ट्याब्लेट",
                "Uses_nepali": "ज्वरोको उपचार, पीडा राहत",
                "Side_effects_nepali": ["वाकवाकी", "बान्ता", "पेट दुखाइ", "अँध्यारो पिसाब", "थकान"]
            },
            "note": "Demo data with fallback translation"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
