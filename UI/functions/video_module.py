import pickle
import cv2
import mediapipe as mp
import numpy as np
import time

model_dict = pickle.load(open('./model/model.p', 'rb'))
model = model_dict['model']

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {i: chr(97 + i) for i in range(26)}

def process_video_with_output():
    cap = cv2.VideoCapture(0)

    detected_sentence = []
    last_confirmed_char = ""
    current_char = ""

    last_detection_time = time.time()
    stabilization_delay = 2.0  # Added a delay of 2 seconds to wait for sign completion
    stable_char = ""

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

                for hand_landmarks in results.multi_hand_landmarks:
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

                if current_char != stable_char and time.time() - last_detection_time >= stabilization_delay:  # Waiting for sign stabilization
                    stable_char = current_char
                    detected_sentence.append(current_char)
                    last_confirmed_char = current_char
                    last_detection_time = time.time()

        cv2.putText(frame, f"Stable Character: {stable_char}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sentence: {' '.join(detected_sentence)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Sign Language Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video_with_output()
