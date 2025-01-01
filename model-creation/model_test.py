import pickle
import cv2
import mediapipe as mp
import numpy as np
from voice import text_to_speech_and_play
from text_fix import generate_sentences  # Import generate_sentences from text_fix

# Load the model
model_dict = pickle.load(open('./model/model.p', 'rb'))
model = model_dict['model']

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize Mediapipe Hands and Drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Define labels dictionary for mapping predictions to lowercase characters (a-z)
labels_dict = {i: chr(97 + i) for i in range(26)}  # ASCII mapping for a-z

# Variables to store detected sentence and characters
detected_sentence = []
current_char = "" 
last_confirmed_char = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data_aux_list = []
    x_list = []
    y_list = []

    H, W, _ = frame.shape

    # Convert frame to RGB for Mediapipe processing
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []

            # Extract normalized coordinates of hand landmarks
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

            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        current_char_list = [] 

        for data_aux in data_aux_list:
            if len(data_aux) == 42:  # Ensure correct input length for prediction
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = labels_dict[int(prediction[0])]

                # Check if model supports confidence probabilities
                if hasattr(model, "predict_proba"):
                    confidence = model.predict_proba([np.asarray(data_aux)])[0][int(prediction[0])]
                else:
                    confidence = 1.0  # Assume confidence as 100% if probabilities are not supported

                current_char_list.append(f"{predicted_character} ({confidence * 100:.2f}%)")

        current_char = " | ".join(current_char_list).upper()  # Capitalize current character(s)

    else:
        current_char = last_confirmed_char.upper() if last_confirmed_char else "NO HAND DETECTED"

    # Display detected sentence on the frame (capitalized)
    sentence_displayed = ' '.join(detected_sentence).upper()
    cv2.putText(frame, sentence_displayed, (50, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    # Display current character on the frame (capitalized)
    cv2.putText(frame, current_char, (50, H - 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow('Sign Language Detector', frame)

    key = cv2.waitKey(1) & 0xFF
    
    if key == 13:  # Enter key pressed (append character)
        detected_sentence.append(current_char.split(" ")[0])  
        last_confirmed_char = current_char.split(" ")[0] 

    if key == ord('z'):
        input_text = ' '.join(detected_sentence).strip()
        print("Full Sentence:", input_text)
        output = generate_sentences(input_text)
        print("Generated Sentence:", output)
        text_to_speech_and_play(output)
        detected_sentence = []


    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
