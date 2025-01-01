import pickle
import cv2
import mediapipe as mp
import numpy as np

model_dict = pickle.load(open('./model/model.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {i: chr(65 + i) for i in range(26)} # Approach 1 -- Short Better with ASCII

# labels_dict = {
#     0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E',
#     5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
#     10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
#     15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T',
#     20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y',
#     25: 'Z'
# } # Approach 2 -- Long but more readable

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

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        current_char_list = [] 

        for data_aux in data_aux_list:
            if len(data_aux) == 42:
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = labels_dict[int(prediction[0])]

                if hasattr(model, "predict_proba"):
                    confidence = model.predict_proba([np.asarray(data_aux)])[0][int(prediction[0])]
                else:
                    confidence = 1.0  # Assume confidence as 100% if probabilities are not supported

                current_char_list.append(f"{predicted_character} ({confidence * 100:.2f}%)")

        current_char = " | ".join(current_char_list)

    else:
        current_char = last_confirmed_char if last_confirmed_char else "No Hand Detected"

    sentence = ' '.join(detected_sentence)
    cv2.putText(frame, sentence, (50, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.putText(frame, current_char, (50, H - 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow('Sign Language Detector', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 13:  # Enter key pressed
        detected_sentence.append(current_char.split(" ")[0])  
        last_confirmed_char = current_char.split(" ")[0] 

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
