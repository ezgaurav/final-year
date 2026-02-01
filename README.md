# Medicine Detection AI Web App

A complete Medicine Detection Web Application that uses YOLOv8 model for OCR detection of medicine labels and provides side effects information with **Nepali translation**.

![Medicine Detection AI](https://img.shields.io/badge/AI-Medicine%20Detection-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

## 🎯 Features

- **🔍 Search Bar**: Search medicines by name with fuzzy matching
- **📷 Photo Upload**: Upload medicine images from device
- **📸 Camera Capture**: Capture medicine photos directly using device camera
- **🌐 Bilingual Results**: Display medicine info + side effects in **English AND Nepali**
- **🤖 AI Detection**: YOLOv8 model trained to detect brand name, dosage, and generic name
- **💊 Medicine Database**: 4000+ medicines with detailed side effects information

## 🛠️ Tech Stack

- **Frontend**: React.js 18.2
- **Backend**: Python FastAPI
- **ML Model**: YOLOv8 (Ultralytics) with PyTorch
- **OCR**: EasyOCR
- **Database**: JSON (drug_data.json, drug_data2.json)
- **Translation**: deep-translator library for Nepali translation

## 📁 Project Structure

```
ezgaurav/final-year/
├── backend/
│   ├── app.py                 # FastAPI server with all endpoints
│   ├── model_handler.py       # Load and run YOLO model
│   ├── database_handler.py    # Read drug database JSON files
│   ├── ocr_handler.py         # Extract text from YOLO bounding boxes
│   ├── translator.py          # Nepali translation using deep-translator
│   ├── requirements.txt       # Python dependencies
│   └── models/
│       └── yolov8n.pt         # YOLO model file (6.4MB)
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js             # Main React app
│   │   ├── App.css            # Styling
│   │   ├── index.js           # Entry point
│   │   ├── components/
│   │   │   ├── SearchBar.js   # Search functionality
│   │   │   ├── ImageUpload.js # Photo upload component
│   │   │   ├── Camera.js      # Camera capture component
│   │   │   └── Results.js     # Display results (English + Nepali)
│   │   └── services/
│   │       └── api.js         # API calls to backend
│   └── package.json
├── data/
│   ├── drug_data.json         # Medicine database (4.6MB)
│   ├── drug_data2.json        # Additional medicine database (3.4MB)
│   ├── classes.txt            # Model classes
│   └── notes.json             # Model metadata
├── README.md                  # This file
└── run.sh                     # One-click start script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- pip
- npm

### One-Click Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/ezgaurav/final-year.git
cd final-year

# Run the startup script
./run.sh
```

The script will:
1. Install backend dependencies
2. Install frontend dependencies
3. Start backend server on http://localhost:8000
4. Start frontend server on http://localhost:3000

### Manual Setup

#### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

#### Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will be available at: http://localhost:3000

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/detect` | POST | Upload image, run YOLO detection, return results |
| `/api/camera` | POST | Handle camera capture |
| `/api/search` | GET | Search medicine by name |
| `/api/medicine/{name}` | GET | Get medicine details + side effects |
| `/api/translate` | POST | Translate text to Nepali |
| `/api/medicines/list` | GET | Get all medicine names |
| `/api/demo/paracetamol` | GET | Demo endpoint with hardcoded data |

## 🎮 How to Use

1. **Search Method**: Type the medicine name in the search bar and click "Search"
2. **Upload Method**: Click "Upload Image" and select a photo of the medicine
3. **Camera Method**: Click "Use Camera" to capture a photo directly
4. **Demo Method**: Click "Try Demo" to see sample data with Paracetamol

## 🧠 YOLO Model Details

The YOLOv8 model (`yolov8n.pt`) is trained to detect 3 classes:

- **Class 0**: Brand name
- **Class 1**: Dosage
- **Class 2**: Generic name

### Model Accuracy
- Trained on 59-60 images
- Accuracy: 60-70%
- Confidence threshold: 0.25 (default)

### Fallback Strategy
If YOLO detection fails or confidence is low:
1. Full image OCR using EasyOCR
2. Fuzzy string matching for database lookup
3. Manual search option available

## 🌐 Translation Feature

All results are automatically translated to Nepali using the `deep-translator` library:

- Medicine name → औषधि नाम
- Uses → प्रयोग
- Side effects → साइड इफेक्ट

Example:
```
English: "Paracetamol 500mg Tablet"
Nepali: "पारासिटामोल ५००mg ट्याब्लेट"
```

## 📊 Database

Two JSON files containing medicine information:

- `drug_data.json`: 4.6MB, ~2000 medicines
- `drug_data2.json`: 3.4MB, ~1500 medicines

Each medicine entry contains:
```json
{
  "Medicine_name": "Medicine Name",
  "Uses": "Treatment description",
  "Side_effects": ["Effect 1", "Effect 2", ...]
}
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Module not found errors
```bash
cd backend
pip install -r requirements.txt --upgrade
```

**Problem**: CUDA/GPU errors
- The app is configured to use CPU by default
- For GPU support, ensure CUDA is properly installed

### Frontend Issues

**Problem**: npm install fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: CORS errors
- Ensure backend is running on port 8000
- Check that frontend proxy is configured in package.json

### Camera Issues

**Problem**: Camera not working
- Grant camera permissions in browser
- Camera only works on localhost or HTTPS
- Try using Chrome or Firefox

## 🔒 Security

- Input validation on all API endpoints
- File upload size limits
- CORS configured for security
- No sensitive data storage

## 📝 Development Notes

### Adding New Medicines

Add entries to `data/drug_data.json` or `data/drug_data2.json`:

```json
"Medicine Key": {
  "Medicine_name": "Medicine Name",
  "Uses": "Uses description",
  "Side_effects": ["Effect 1", "Effect 2"]
}
```

### Training Your Own Model

1. Collect and label images with medicine labels
2. Export dataset in YOLO format
3. Train using Ultralytics YOLOv8:
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8n.yaml')
   model.train(data='dataset.yaml', epochs=100)
   ```
4. Replace `backend/models/yolov8n.pt` with your trained model

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational purposes as part of a final year project.

## 👨‍💻 Author

- GitHub: [@ezgaurav](https://github.com/ezgaurav)

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- Medicine data from medical databases
- EasyOCR for text extraction
- deep-translator for Nepali translations

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This app is designed for educational purposes. Always consult healthcare professionals for medical advice.