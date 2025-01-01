import os
import pickle
import mediapipe as mp
import cv2
from tqdm import tqdm  

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
expected_num_landmarks = 21

DATA_DIR = './augmented-data'
data = []
labels = []  

for dir_ in os.listdir(DATA_DIR):

    for img_path in tqdm(os.listdir(os.path.join(DATA_DIR, dir_)), 
                         desc=f"Processing {dir_} images", unit="image"):
        
        data_aux = []
        x_ = []
        y_ = []

        img = cv2.imread(os.path.join(DATA_DIR, dir_, img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                if len(x_) == expected_num_landmarks:
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                    data.append(data_aux)
                    labels.append(dir_)
                else:
                    print(f"\nSkipping image {img_path} because it doesn't have the correct number of landmarks.\n")
                    continue 
        else:
            print(f"\nSkipping image {img_path} because no hand was detected.\n")

print("\nSaving dataset...")
with open('./datasets/dataset.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print("\nData creation was successful! Now you can train the classifier.")
