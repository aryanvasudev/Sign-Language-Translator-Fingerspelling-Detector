from flask import Flask, render_template, jsonify, request, Response
import cv2
import mediapipe as mp
import numpy as np
import pickle
import time
from functions.text_fix import generate_sentences
import os

app = Flask(__name__)

# Load the ML model and initialize MediaPipe
model_dict = pickle.load(open('./model/model.p', 'rb'))
model = model_dict['model']
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
labels_dict = {i: chr(97 + i) for i in range(26)}

# Global variables to store detection state
detected_sentence = []
is_recording = False
last_confirmed_char = ""
last_detection_time = time.time()
stabilization_delay = 2.0
stable_char = ""

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
                
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        current_char_list = []
        for data_aux in data_aux_list:
            if len(data_aux) == 42:
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = labels_dict[int(prediction[0])]
                
                if hasattr(model, "predict_proba"):
                    confidence = model.predict_proba([np.asarray(data_aux)])[0][int(prediction[0])] * 100
                else:
                    confidence = 100.0
                    
                current_char_list.append(f"{predicted_character} ({confidence:.2f}%)")

        if current_char_list:
            current_char = current_char_list[0].split()[0].upper()
            if current_char != stable_char and time.time() - last_detection_time >= stabilization_delay:
                stable_char = current_char
                if is_recording:
                    detected_sentence.append(current_char)
                last_confirmed_char = current_char
                last_detection_time = time.time()

        # Add text overlays
        cv2.putText(frame, f"Stable Character: {stable_char}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sentence: {' '.join(detected_sentence)}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert frame to bytes for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording, detected_sentence
    is_recording = True
    detected_sentence = []  # Reset the sentence when starting new recording
    return jsonify({'status': 'success'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording, detected_sentence
    is_recording = False
    
    # Join the detected characters and convert to meaningful sentence
    raw_text = ' '.join(detected_sentence)
    meaningful_sentence = generate_sentences(raw_text)
    
    return jsonify({
        'status': 'success',
        'raw_text': raw_text,
        'meaningful_sentence': meaningful_sentence
    })

@app.route('/get_current_prediction')
def get_current_prediction():
    global stable_char
    return jsonify({'prediction': stable_char})

if __name__ == '__main__':
    app.run(debug=True)
