# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SignBridge** — An ASL (American Sign Language) fingerspelling translator that bridges communication gaps by converting sign language gestures to text and vice versa. The system uses MediaPipe for hand tracking, a RandomForestClassifier for gesture recognition, OpenAI API for text correction, and ElevenLabs API for text-to-speech.

**Built on Python 3.11** (Python 3.9+ supported)

## Quick Start Commands

### Running the Application
```bash
# From project root, navigate to UI folder
cd UI

# Run the Flask app (development)
python app.py

# Or with gunicorn (production)
gunicorn --bind 0.0.0.0:5000 app:app
```

The app will start at `http://127.0.0.1:5000/` (Google Chrome recommended).

### Installing Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing)
pip install -r requirements-dev.txt
```

### Running Tests
```bash
# From project root
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=UI
```

### Docker
```bash
# Build image
docker build -t sign-translator .

# Run with docker-compose
docker-compose up
```

### Environment Setup
Create a `.env` file in the project root based on `.env.example`:
```
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Optional: Override detection settings
STABILITY_THRESHOLD=5
STABILIZATION_DELAY=2.0
MIN_DETECTION_CONFIDENCE=0.3
```

## Architecture

### Core Processing Pipeline

**Sign-to-Text Flow:**
1. **Video Capture** (`UI/app.py:generate_frames()`) - OpenCV captures webcam feed
2. **Hand Detection** - MediaPipe extracts 21 hand landmarks
3. **Feature Extraction** (`process_hand_landmarks()`) - Normalized 42D feature vector
4. **Prediction** (`predict_character()`) - RandomForestClassifier predicts character
5. **Stabilization** (`SignLanguageDetector.check_sign_stability()`) - 5 consecutive identical predictions within 1s window
6. **Confirmation** - 2-second delay before accepting new character
7. **Text Correction** (`UI/functions/text_fix.py`) - OpenAI API corrects spacing/grammar
8. **Speech Output** (`UI/functions/voice.py`) - ElevenLabs API converts to speech

### Key Classes

**`SignLanguageDetector`** (`UI/app.py`) - Main detection state manager:
- Encapsulates all detection state (replaces global variables)
- Methods: `start_recording()`, `stop_recording()`, `check_sign_stability()`, `process_stable_prediction()`
- Thread-safe design with instance-level state

### Configuration Constants

All configurable via environment variables in `UI/app.py`:
```python
STABILITY_THRESHOLD = 5       # Consecutive predictions needed
STABILITY_TIME_WINDOW = 1.0   # Seconds for stability check
STABILIZATION_DELAY = 2.0     # Delay before new character
MIN_DETECTION_CONFIDENCE = 0.3 # MediaPipe confidence
MAX_TEXT_LENGTH = 500          # Max input text length
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/health` | GET | Health check (Docker/k8s) |
| `/video_feed` | GET | Live video stream |
| `/start_recording` | POST | Begin sign capture |
| `/stop_recording` | POST | End capture, process text |
| `/get_current_prediction` | GET | Current stable character |
| `/speak_text` | POST | Text-to-speech |
| `/convert_text` | POST | Text to sign images |
| `/convert_speech_to_sign` | POST | Speech to sign images |

**Rate Limiting**: `/stop_recording` and `/convert_text` limited to 10 requests/minute (when flask-limiter installed).

### Model Training Pipeline

**Run in this exact order from the `model-creation` folder:**

1. `python collect_images.py` - Capture 500 images per class (0-26)
2. `python augment_data.py` - 5x augmentation
3. `python create_Dataset.py` - Extract MediaPipe landmarks to pickle
4. `python train_classifier.py` - Train RandomForest, save to `model/model.p`

### Feature Extraction (Critical)

```python
def process_hand_landmarks(hand_landmarks) -> list[float]:
    x_coords = [lm.x for lm in hand_landmarks.landmark]
    y_coords = [lm.y for lm in hand_landmarks.landmark]
    min_x, min_y = min(x_coords), min(y_coords)

    features = []
    for lm in hand_landmarks.landmark:
        features.append(lm.x - min_x)
        features.append(lm.y - min_y)
    return features  # 42D vector
```

## Project Structure

```
Sign-Language-Translator/
├── UI/
│   ├── app.py              # Flask app with SignLanguageDetector class
│   ├── functions/
│   │   ├── text_fix.py     # OpenAI text correction (new API)
│   │   ├── voice.py        # ElevenLabs TTS
│   │   ├── text_to_sign.py # Text to sign images
│   │   └── speech_to_text.py # Speech recognition
│   ├── static/
│   │   ├── css/style.css   # SignBridge design (~1200 lines)
│   │   └── js/main.js      # Frontend controller with state management
│   └── templates/
│       └── index.html      # SignBridge UI with hero, panels, features
├── model/
│   └── model.p             # Trained RandomForest model
├── datasets/
│   ├── dataset.pickle      # Training data
│   └── letter_images/      # A-Z sign images
├── model-creation/         # Training scripts
├── tests/                  # Pytest tests
├── Dockerfile              # Container build
├── docker-compose.yml      # Dev orchestration
├── requirements.txt        # Production deps
└── requirements-dev.txt    # Dev/test deps
```

## Features Added

### Logging
- File logging to `UI/app.log`
- Console logging with timestamps
- Log levels: INFO for normal, ERROR for failures

### Rate Limiting
- Optional flask-limiter integration
- 10 requests/minute on expensive endpoints
- Gracefully disabled if not installed

### Graceful Shutdown
- Signal handlers for SIGINT/SIGTERM
- Resource cleanup (MediaPipe, camera)
- atexit registration

### Frontend Design (SignBridge)
- **Design Aesthetic**: Organic Human-Centered + Soft Editorial
- **Typography**: Fraunces (display) + Outfit (body) from Google Fonts
- **Color Palette**: Cream background (#faf8f5), deep teal primary (#1d5c5c), warm coral accent (#e07a5f)
- **Visual Elements**:
  - Glass-morphism panels with backdrop blur
  - Animated breathing background
  - Floating hand SVG decorations
  - Recording indicator with pulse animation
  - Progress bar for sign display sequence
- **UI Features**:
  - Loading overlay with animated hand SVG
  - Toast notifications (success/error/info)
  - Character count with warning states
  - Auto-resizing textarea
- **Accessibility**:
  - Full ARIA labels and roles
  - `prefers-reduced-motion` support
  - `prefers-contrast` high contrast mode
  - Keyboard navigation focus styles
  - Screen reader announcements
- **Keyboard Shortcuts**: Ctrl/Cmd+Enter (convert), Escape (stop), Space (start when focused)

### Input Validation
- Max 500 characters for text
- Letters and spaces only
- JSON validation on POST

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_app.py::TestConvertTextEndpoint -v

# Run with coverage report
pytest tests/ --cov=UI --cov-report=html
```

## Docker Usage

```bash
# Development (with hot reload)
docker-compose up

# Production build
docker build -t sign-translator .
docker run -p 5000:5000 --env-file .env sign-translator

# Note: Camera access requires device mapping on Linux
# On Windows/Mac, run natively for camera features
```

## Troubleshooting

**"Model file not found"**: Ensure `model/model.p` exists. Run from correct directory.

**"API key not found"**: Create `.env` file with required keys.

**Camera not detected**: Check permissions, ensure no other app is using webcam.

**Rate limiting errors**: Wait 1 minute or disable flask-limiter.

**OpenAI errors**: Check API key validity, rate limits, account credits.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd+Enter` | Convert text (when in textarea) |
| `Escape` | Stop recording |
| `Space` | Start recording (when record button focused) |
| `Tab` | Keyboard navigation (adds focus styles) |

## Label Encoding

Classes 0-25 map to letters 'a'-'z' (lowercase internally, displayed uppercase).
Formula: `chr(97 + class_index)`
