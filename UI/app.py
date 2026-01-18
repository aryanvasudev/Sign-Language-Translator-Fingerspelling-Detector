"""
Sign Language Translator - Flask Application

This module provides a Flask-based web application for translating
American Sign Language (ASL) fingerspelling to text and vice versa.
"""

from flask import Flask, render_template, jsonify, request, Response
import cv2
import mediapipe as mp
import numpy as np
import pickle
import time
import os
import sys
import signal
import atexit
import logging
from typing import Optional, Generator, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from functions.text_fix import generate_sentences
from functions.voice import text_to_speech_and_play
from functions.text_to_sign import text_to_sign_language
from functions.speech_to_text import speech_to_text

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Model and detection settings
MIN_DETECTION_CONFIDENCE: float = float(os.getenv('MIN_DETECTION_CONFIDENCE', '0.3'))
NUM_HAND_LANDMARKS: int = 21
FEATURE_VECTOR_SIZE: int = 42  # 21 landmarks * 2 coordinates (x, y)

# Stabilization settings (can be configured via environment variables)
STABILITY_THRESHOLD: int = int(os.getenv('STABILITY_THRESHOLD', '5'))
STABILITY_TIME_WINDOW: float = float(os.getenv('STABILITY_TIME_WINDOW', '1.0'))
STABILIZATION_DELAY: float = float(os.getenv('STABILIZATION_DELAY', '2.0'))

# Input validation
MAX_TEXT_LENGTH: int = 500

# Paths - resolved relative to this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'model.p')
LOG_FILE = os.path.join(BASE_DIR, 'app.log')

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# FLASK APPLICATION SETUP
# =============================================================================

app = Flask(__name__)

# Try to import and configure rate limiting
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    RATE_LIMITING_ENABLED = True
    logger.info("Rate limiting enabled")
except ImportError:
    logger.warning("flask-limiter not installed. Rate limiting disabled. Install with: pip install flask-limiter")
    RATE_LIMITING_ENABLED = False
    limiter = None


# =============================================================================
# MODEL AND MEDIAPIPE INITIALIZATION
# =============================================================================

def load_model() -> Any:
    """Load the trained ML model from pickle file.

    Returns:
        The loaded model object.

    Raises:
        SystemExit: If model cannot be loaded.
    """
    try:
        logger.info(f"Loading model from: {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            model_dict = pickle.load(f)
        logger.info("Model loaded successfully")
        return model_dict['model']
    except FileNotFoundError:
        logger.error(f"Model file not found at: {MODEL_PATH}")
        logger.error("Please ensure the model file exists. Run train_classifier.py to generate it.")
        sys.exit(1)
    except (pickle.UnpicklingError, KeyError) as e:
        logger.error(f"Error loading model - file may be corrupted: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error loading model: {e}")
        sys.exit(1)


def initialize_mediapipe() -> mp.solutions.hands.Hands:
    """Initialize MediaPipe hands detection.

    Returns:
        Configured MediaPipe Hands object.
    """
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE
    )
    logger.info(f"MediaPipe initialized with confidence threshold: {MIN_DETECTION_CONFIDENCE}")
    return hands


# Initialize model and MediaPipe
model = load_model()
mp_hands = mp.solutions.hands
hands = initialize_mediapipe()

# Label mapping: 0-25 -> a-z
labels_dict = {i: chr(97 + i) for i in range(26)}


# =============================================================================
# SIGN LANGUAGE DETECTOR CLASS
# =============================================================================

class SignLanguageDetector:
    """Encapsulates the state and logic for sign language detection.

    This class manages the detection state, stability checking, and
    sentence building for the sign-to-text conversion process.
    """

    def __init__(self) -> None:
        """Initialize the detector with default state."""
        self.reset()

    def reset(self) -> None:
        """Reset the detector state to initial values."""
        self.detected_sentence: list[str] = []
        self.is_recording: bool = False
        self.last_confirmed_char: str = ""
        self.last_detection_time: float = time.time()
        self.stable_char: str = ""
        self.current_meaningful_sentence: str = ""
        self.stability_buffer: list[tuple[str, float]] = []

    def start_recording(self) -> None:
        """Start recording mode and reset sentence."""
        self.is_recording = True
        self.detected_sentence = []
        self.stability_buffer = []
        self.last_confirmed_char = ""
        self.stable_char = ""
        logger.info("Recording started")

    def stop_recording(self) -> tuple[str, str]:
        """Stop recording and generate meaningful sentence.

        Returns:
            Tuple of (raw_text, meaningful_sentence)
        """
        self.is_recording = False
        raw_text = ' '.join(self.detected_sentence)

        if raw_text:
            try:
                self.current_meaningful_sentence = generate_sentences(raw_text)
                logger.info(f"Generated sentence: {self.current_meaningful_sentence}")
            except Exception as e:
                logger.error(f"Error generating sentence: {e}")
                self.current_meaningful_sentence = raw_text
        else:
            self.current_meaningful_sentence = ""

        logger.info(f"Recording stopped. Raw: '{raw_text}', Processed: '{self.current_meaningful_sentence}'")
        return raw_text, self.current_meaningful_sentence

    def check_sign_stability(self, prediction: str) -> tuple[bool, Optional[str]]:
        """Check if a sign prediction is stable over time.

        Args:
            prediction: The predicted character.

        Returns:
            Tuple of (is_stable, stable_prediction or None)
        """
        current_time = time.time()

        # Remove old predictions outside the time window
        self.stability_buffer = [
            (pred, t) for pred, t in self.stability_buffer
            if current_time - t < STABILITY_TIME_WINDOW
        ]

        # Add new prediction
        self.stability_buffer.append((prediction, current_time))

        # Check if we have enough predictions and they're all the same
        if len(self.stability_buffer) >= STABILITY_THRESHOLD:
            recent_predictions = [pred for pred, _ in self.stability_buffer[-STABILITY_THRESHOLD:]]
            if all(pred == recent_predictions[0] for pred in recent_predictions):
                return True, recent_predictions[0]

        return False, None

    def process_stable_prediction(self, prediction: str) -> None:
        """Process a stable prediction and add to sentence if appropriate.

        Args:
            prediction: The stable predicted character.
        """
        current_time = time.time()
        self.stable_char = prediction

        # Add to sentence if recording and enough time has passed
        if (self.is_recording and
            prediction != self.last_confirmed_char and
            current_time - self.last_detection_time >= STABILIZATION_DELAY):

            self.detected_sentence.append(prediction)
            self.last_confirmed_char = prediction
            self.last_detection_time = current_time
            logger.debug(f"Added character: {prediction}, Sentence: {self.detected_sentence}")


# Create global detector instance
detector = SignLanguageDetector()


# =============================================================================
# VIDEO PROCESSING FUNCTIONS
# =============================================================================

def process_hand_landmarks(hand_landmarks) -> list[float]:
    """Extract normalized feature vector from hand landmarks.

    Args:
        hand_landmarks: MediaPipe hand landmarks object.

    Returns:
        List of normalized x, y coordinates (42 values).
    """
    x_coords = [lm.x for lm in hand_landmarks.landmark]
    y_coords = [lm.y for lm in hand_landmarks.landmark]

    min_x, min_y = min(x_coords), min(y_coords)

    features = []
    for lm in hand_landmarks.landmark:
        features.append(lm.x - min_x)
        features.append(lm.y - min_y)

    return features


def predict_character(features: list[float]) -> tuple[str, float]:
    """Predict character from feature vector.

    Args:
        features: Normalized feature vector (42 values).

    Returns:
        Tuple of (predicted_character, confidence)
    """
    if len(features) != FEATURE_VECTOR_SIZE:
        return "", 0.0

    prediction = model.predict([np.asarray(features)])
    predicted_char = labels_dict[int(prediction[0])]

    # Get confidence if available
    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba([np.asarray(features)])[0][int(prediction[0])] * 100
    else:
        confidence = 100.0

    return predicted_char.upper(), confidence


def draw_overlays(frame: np.ndarray, stable_char: str,
                  sentence: list[str], is_stable: bool) -> np.ndarray:
    """Draw text overlays on the video frame.

    Args:
        frame: OpenCV image frame.
        stable_char: Currently stable character.
        sentence: List of detected characters.
        is_stable: Whether current detection is stable.

    Returns:
        Frame with overlays drawn.
    """
    # Stable character
    cv2.putText(frame, f"Stable Character: {stable_char}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Current sentence
    cv2.putText(frame, f"Sentence: {' '.join(sentence)}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Stability status
    status_text = "Stable" if is_stable else "Unstable"
    status_color = (0, 255, 0) if is_stable else (0, 0, 255)
    cv2.putText(frame, f"Sign Status: {status_text}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

    return frame


def create_error_frame(message: str) -> bytes:
    """Create a frame with an error message.

    Args:
        message: Error message to display.

    Returns:
        JPEG encoded error frame.
    """
    # Create a dark frame with error message
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (30, 30, 30)  # Dark gray background

    # Add error message
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(message, font, 0.7, 2)[0]
    text_x = (640 - text_size[0]) // 2
    text_y = (480 + text_size[1]) // 2
    cv2.putText(frame, message, (text_x, text_y), font, 0.7, (200, 200, 200), 2)

    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes() if ret else b''


def generate_frames() -> Generator[bytes, None, None]:
    """Generate video frames with sign language detection.

    Yields:
        JPEG encoded frames for streaming.
    """
    cap = None
    consecutive_failures = 0
    max_failures = 30  # Allow up to 30 consecutive failures before reconnecting
    reconnect_attempts = 0
    max_reconnect_attempts = 5

    while reconnect_attempts < max_reconnect_attempts:
        try:
            # Try to open camera
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.error("Failed to open camera")
                    reconnect_attempts += 1
                    error_frame = create_error_frame(f"Camera not available. Retrying... ({reconnect_attempts}/{max_reconnect_attempts})")
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                    time.sleep(2)
                    continue

                logger.info("Camera opened successfully")
                consecutive_failures = 0
                reconnect_attempts = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    consecutive_failures += 1
                    logger.warning(f"Failed to read frame ({consecutive_failures}/{max_failures})")

                    if consecutive_failures >= max_failures:
                        logger.error("Too many consecutive frame failures, reconnecting camera...")
                        if cap is not None:
                            cap.release()
                            cap = None
                        reconnect_attempts += 1
                        break  # Break inner loop to reconnect

                    # Yield a placeholder frame while waiting
                    time.sleep(0.1)
                    continue

                # Reset failure counter on successful read
                consecutive_failures = 0

                # Convert to RGB for MediaPipe
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                # Process detected hands
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                        )

                        # Extract features and predict
                        features = process_hand_landmarks(hand_landmarks)

                        if len(features) == FEATURE_VECTOR_SIZE:
                            predicted_char, confidence = predict_character(features)

                            # Check stability
                            is_stable, stable_pred = detector.check_sign_stability(predicted_char)

                            if is_stable and stable_pred:
                                detector.process_stable_prediction(stable_pred)

                            # Draw overlays
                            is_buffer_stable = len(detector.stability_buffer) >= STABILITY_THRESHOLD
                            frame = draw_overlays(
                                frame,
                                detector.stable_char,
                                detector.detected_sentence,
                                is_buffer_stable
                            )
                            break  # Only process first detected hand

                # Encode and yield frame
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        except GeneratorExit:
            # Client disconnected, clean up
            logger.info("Client disconnected from video feed")
            break
        except Exception as e:
            logger.error(f"Error in video processing: {e}")
            reconnect_attempts += 1
            if cap is not None:
                cap.release()
                cap = None
            time.sleep(1)

    # Final cleanup
    if cap is not None:
        cap.release()
        logger.info("Camera released")


# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for Docker/Kubernetes."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'rate_limiting': RATE_LIMITING_ENABLED
    })


@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/start_recording', methods=['POST'])
def start_recording():
    """Start recording sign language gestures."""
    detector.start_recording()
    return jsonify({'status': 'success', 'message': 'Recording started'})


@app.route('/stop_recording', methods=['POST'])
def stop_recording_route():
    """Stop recording and process the detected sentence."""
    raw_text, meaningful_sentence = detector.stop_recording()
    return jsonify({
        'status': 'success',
        'raw_text': raw_text,
        'meaningful_sentence': meaningful_sentence
    })


# Apply rate limiting only if available
if RATE_LIMITING_ENABLED and limiter:
    stop_recording_route = limiter.limit("10 per minute")(stop_recording_route)


@app.route('/get_current_prediction')
def get_current_prediction():
    """Get the currently stable character prediction."""
    return jsonify({'prediction': detector.stable_char})


@app.route('/speak_text', methods=['POST'])
def speak_text():
    """Convert the current meaningful sentence to speech."""
    try:
        if detector.current_meaningful_sentence:
            text_to_speech_and_play(detector.current_meaningful_sentence)
            logger.info(f"Spoke text: {detector.current_meaningful_sentence}")
            return jsonify({
                'status': 'success',
                'message': 'Audio played successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No text available to speak. Please record some signs first.'
            })
    except Exception as e:
        logger.error(f"Error in speak_text: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to play audio: {str(e)}'
        })


@app.route('/convert_text', methods=['POST'])
def convert_text():
    """Convert input text to sign language images."""
    # Validate request
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Request must be JSON'
        }), 400

    text = request.json.get('text', '').strip()

    # Validate input
    if not text:
        return jsonify({
            'status': 'error',
            'message': 'No text provided. Please enter some text to convert.'
        })

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({
            'status': 'error',
            'message': f'Text too long. Maximum {MAX_TEXT_LENGTH} characters allowed.'
        })

    # Filter to only allow letters and spaces
    filtered_text = ''.join(c for c in text if c.isalpha() or c.isspace())

    if not filtered_text:
        return jsonify({
            'status': 'error',
            'message': 'Please enter English letters only (A-Z).'
        })

    try:
        images_data = text_to_sign_language(filtered_text)
        logger.info(f"Converted text to sign: {filtered_text}")
        return jsonify({
            'status': 'success',
            'message': 'Text converted successfully',
            'images': images_data
        })
    except Exception as e:
        logger.error(f"Error in convert_text: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to convert text: {str(e)}'
        })


# Apply rate limiting only if available
if RATE_LIMITING_ENABLED and limiter:
    convert_text = limiter.limit("10 per minute")(convert_text)


@app.route('/convert_speech_to_sign', methods=['POST'])
def convert_speech_to_sign():
    """Convert speech input to sign language images."""
    try:
        # Convert speech to text
        logger.info("Starting speech recognition...")
        text = speech_to_text()

        if text is None:
            return jsonify({
                'status': 'error',
                'message': 'Could not understand speech. Please try again and speak clearly.'
            })

        logger.info(f"Recognized speech: {text}")

        # Convert text to sign language
        images_data = text_to_sign_language(text)

        return jsonify({
            'status': 'success',
            'text': text,
            'images': images_data
        })

    except Exception as e:
        logger.error(f"Error in convert_speech_to_sign: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Speech conversion failed: {str(e)}'
        })


# =============================================================================
# CLEANUP AND SHUTDOWN HANDLERS
# =============================================================================

def cleanup() -> None:
    """Clean up resources on shutdown."""
    global hands
    try:
        if hands:
            hands.close()
            logger.info("MediaPipe hands closed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def signal_handler(sig, frame) -> None:
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)


# Register cleanup handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    logger.info("Starting Sign Language Translator...")
    logger.info(f"Model path: {MODEL_PATH}")
    logger.info(f"Stability threshold: {STABILITY_THRESHOLD}")
    logger.info(f"Stabilization delay: {STABILIZATION_DELAY}s")

    # Run the Flask app
    # Note: debug=True is for development only
    # For production, use a WSGI server like gunicorn
    app.run(debug=False, threaded=True)
