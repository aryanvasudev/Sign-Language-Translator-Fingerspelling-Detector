from flask import Flask, render_template, jsonify, request, Response
import cv2
import mediapipe as mp
import numpy as np
import pickle
import time
from functions.text_fix import generate_sentences
from functions.voice import text_to_speech_and_play
from functions.text_to_sign import text_to_sign_language
import os
from functions.speech_to_text import speech_to_text


app = Flask(__name__)

# Load the ML model and initialize MediaPipe
model_dict = pickle.load(open('./model/model.p', 'rb'))
model = model_dict['model']
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
labels_dict = {i: chr(97 + i) for i in range(26)}


# Global variables
detected_sentence = []
is_recording = False
last_confirmed_char = ""
last_detection_time = time.time()
stabilization_delay = 2.0
stable_char = ""
current_meaningful_sentence = ""
stability_buffer = []
STABILITY_THRESHOLD = 5
STABILITY_TIME_WINDOW = 1.0

# Function to check sign stability
def check_sign_stability(prediction):
    global stability_buffer
    current_time = time.time()
    stability_buffer = [(pred, t) for pred, t in stability_buffer 
                       if current_time - t < STABILITY_TIME_WINDOW]
    stability_buffer.append((prediction, current_time))
    if len(stability_buffer) >= STABILITY_THRESHOLD:
        recent_predictions = [pred for pred, _ in stability_buffer[-STABILITY_THRESHOLD:]]
        if all(pred == recent_predictions[0] for pred in recent_predictions):
            return True, recent_predictions[0]
    return False, None

# Function to generate frames
def generate_frames():
    global is_recording, detected_sentence, last_confirmed_char, last_detection_time, stable_char
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data_aux_list = []
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                data_aux = []
                x_ = []
                y_ = []
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

                data_aux_list.append(data_aux)
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        current_char_list = []
        for data_aux in data_aux_list:
            if len(data_aux) == 42:
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = labels_dict[int(prediction[0])]
                
                if hasattr(model, "predict_proba"):
                    confidence = model.predict_proba([np.asarray(data_aux)])[0][int(prediction[0])] * 100
                else:
                    confidence = 100.0
                    
                current_char_list.append((predicted_character, confidence))

        if current_char_list:
            current_char, confidence = current_char_list[0]
            current_char = current_char.upper()
            
            is_stable, stable_prediction = check_sign_stability(current_char)
            if is_stable and time.time() - last_detection_time >= stabilization_delay:
                stable_char = stable_prediction
                if is_recording and stable_char != last_confirmed_char:
                    detected_sentence.append(stable_char)
                    last_confirmed_char = stable_char
                    last_detection_time = time.time()

        cv2.putText(frame, f"Stable Character: {stable_char}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sentence: {' '.join(detected_sentence)}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        stability_status = "Stable" if len(stability_buffer) >= STABILITY_THRESHOLD else "Unstable"
        cv2.putText(frame, f"Sign Status: {stability_status}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0) if stability_status == "Stable" else (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to the video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to start and stop recording
@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording, detected_sentence, stability_buffer
    is_recording = True
    detected_sentence = []
    stability_buffer = []
    return jsonify({'status': 'success'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording, detected_sentence, current_meaningful_sentence
    is_recording = False
    raw_text = ' '.join(detected_sentence)
    current_meaningful_sentence = generate_sentences(raw_text)
    return jsonify({
        'status': 'success',
        'raw_text': raw_text,
        'meaningful_sentence': current_meaningful_sentence
    })

# Route to get the current prediction
@app.route('/get_current_prediction')
def get_current_prediction():
    global stable_char
    return jsonify({'prediction': stable_char})

# Route to speak the current meaningful sentence
@app.route('/speak_text', methods=['POST'])
def speak_text():
    global current_meaningful_sentence
    try:
        if current_meaningful_sentence:
            text_to_speech_and_play(current_meaningful_sentence)
            return jsonify({'status': 'success', 'message': 'Audio played successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'No text to speak'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to convert text to sign language
@app.route('/convert_text', methods=['POST'])
def convert_text():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'status': 'error', 'message': 'No input found'})
    try:
        images_data = text_to_sign_language(text)
        return jsonify({
            'status': 'success', 
            'message': 'Text converted successfully',
            'images': images_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
# Route to convert speech to sign language
@app.route('/convert_speech_to_sign', methods=['POST'])
def convert_speech_to_sign():
    try:
        # First convert speech to text
        text = speech_to_text()
        
        if text is None:
            return jsonify({
                'status': 'error',
                'message': 'Could not understand speech'
            })
            
        # Convert the text to sign language
        images_data = text_to_sign_language(text)
        
        return jsonify({
            'status': 'success',
            'text': text,
            'images': images_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
