# Documentation for Sign Language Translator Project

## 📁 **Table of Contents**

- [Introduction](#-Introduction)
- [User Guide](#-user-Guide)
- [Technical Details](#-Technical-Details)
- [Integration with APIs](#-Integration-with-APIs)
- [UI/UX Design](#-UI/UX-Design)
- [Future Improvements](#-Future-Improvements)
- [Conclusion](#-Conclusion)
- [Appendices](#-Appendices)

## 1. Introduction

The Sign Language Translator project is a groundbreaking initiative designed to facilitate communication between individuals who use American Sign Language (ASL) and those who do not. By translating ASL into text and speech, this project aims to make interactions more accessible and inclusive for everyone. The real-time detection system captures ASL gestures through the webcam using MediaPipe's hand tracking, which identifies key points on the hands. These landmarks are then processed by a `RandomForestClassifier` model that has been trained on a dataset of ASL gestures. The machine learning model predicts the corresponding text output, which is refined through the OpenAI API for accuracy. Finally, the translated text can be converted into speech using the ElevenLabs API, providing both visual and auditory outputs for comprehensive communication. The translator utilizes sophisticated machine learning models and APIs to provide accurate, real-time translations, thus fostering better understanding and interaction across different communities.

## 🌟 **Features**

- 💻 **User-Friendly Interface**: Designed for ease of use on both desktop and mobile platforms, making it accessible to a wide range of users.
- 📄 **API Integration**: Leverages state-of-the-art APIs to enhance the accuracy and efficiency of translations.
- 🦐 **Real-time ASL Fingerspelling Detection**: Detects and translates ASL fingerspelling gestures into text in real-time.
- 🔠 **Text-to-Sign Conversion**: Converts input text into fingerspelling animations, bridging communication gaps for non-ASL speakers.
- 🔊 **Integrated Speech System**: Converts text to speech, making the communication output audible.
- 📂 **Lightweight and User-Friendly**: Optimized for accessibility and ease of use.

## 2. User Guide

### Installation Instructions

#### Prerequisites:

To set up the Sign Language Translator, ensure you have the following:

##### Backend

- **Python**: Version 3.9 or higher, with 3.11 recommended for optimal performance.
- **Libraries**: MediaPipe, scikit-learn, OpenAI API, and ElevenLabs API.

##### Frontend

- **HTML**: Used for the basic structure of the web app.
- **CSS**: Enhances the web app's UI aesthetics.
- **JavaScript**: Facilitates function calls and integrates with the Flask app for responsive interactions.

#### Step-by-Step Installation:

1. **Clone the Repository**: Use GitHub to clone the project repository to your local machine.

   ```bash
   git clone https://github.com/JashanMaan28/Sign-Language-Translator-Fingerspelling-Detector.git
   ```

   Or download the zip file from our GitHub and unzip it. Then navigate to the folder containing all the components. Skip to Step 3 after this.

2. **Navigate to Directory**: Open the terminal and navigate to the project directory.

3. **Install Dependencies**: Execute the command using the Terminal:

   ```bash
   pip install -r requirements.txt
   ```

   This will install all the necessary libraries.

4. **Configure API Keys**: Set up your API keys for OpenAI and ElevenLabs in the `.env` file (create one if necessary). Refer to `.env.example` for guidance.

5. **Run the Application**: Launch the application by navigating to the UI folder and running:

   ```bash
   python app.py
   ```

### Usage

#### Running the Translator:

- **Launch the Application**: Launch `app.py`, and access the app through the provided address, usually `http://127.0.0.1:5000/`, in your preferred browser (Google Chrome recommended for best performance).
- **Use Webcam for Signing**: The application captures ASL gestures through your webcam.
- **View Translations**: The translated text will be displayed on the screen, and speech output will be generated upon respective button clicks, as shown in the demo video on our GitHub repository.

#### Example Use Cases:

- **Facilitating Communication**: Helps non-sign language users understand ASL.
- **Educational Tool**: Assists learners in practicing and improving their ASL skills.
- **Real-Time Translation**: Functions as an effective translation app between users and individuals who are deaf or mute.

### Troubleshooting

#### Common Issues:

- **Camera Detection**: Ensure your webcam is connected and functioning. Check system permissions if the camera is not detected.
- **API Errors**: Confirm that your API keys are correctly entered and that the APIs are accessible from the `.env` file.

#### FAQs:

- **Resetting the Application**: Restart the application by closing and reopening it from the terminal or your code editor.
- **Multiple Sign Languages**: Currently, the translator supports ASL only. Future updates may add support for other sign languages based on user demand.

## 3. Technical Details

### Architecture

The system architecture of the Sign Language Translator comprises several interconnected components:

- **Input Capture**: Utilizes computer vision to capture video input and process hand gestures via MediaPipe.
- **Machine Learning Model**: A `RandomForestClassifier` from the scikit-learn library trained on a dataset of ASL gesture MediaPipe landmarks to predict corresponding text.
- **API Integration**: Integrates OpenAI API for text processing and ElevenLabs API for converting text to speech.

### Technologies Used

- **MediaPipe**: Provides real-time hand tracking and landmark detection to accurately capture sign language gestures.
- **scikit-learn**: Used for developing and training the machine learning model.
- **OpenAI API**: Enhances text processing capabilities to improve translation accuracy.
- **ElevenLabs API**: Converts text output into speech, enabling audible translations.

### Model Training

#### Data Collection and Preprocessing:

- **Data Collection**: ASL gesture data is collected using OpenCV and the MediaPipe framework. OpenCV manages the video capture from the webcam, while MediaPipe provides real-time hand tracking and landmark detection. This combination allows for precise capture of hand movements and gestures.
- **Preprocessing**: The data is normalized, augmented, and cleaned to ensure consistency and reduce noise, improving the model's performance.

#### Model Selection:

- **RandomForestClassifier**: Selected for its balance between performance and simplicity, offering robust accuracy in classifying ASL gestures.

#### Evaluation Metrics:

- **Accuracy**: Measures how often the model correctly predicts the sign language gestures.
- **F1 Score**: Provides a balanced measure of precision and recall, offering insights into the model's performance across different classes.
- **Scores**: Our model achieved an accuracy of 99.8% using our dataset.

### Design Choices and Rationale

- **MediaPipe**: Chosen for its efficient real-time tracking capabilities.
- **RandomForestClassifier**: Preferred due to its ability to handle multiclass classification effectively with minimal hyperparameter tuning.
- **OpenAI and ElevenLabs APIs**: Integrated to leverage state-of-the-art language processing and text-to-speech conversion technologies, ensuring high-quality output.

### Strategies to Address Overfitting and Underfitting

- **Overfitting**: Prevented through data augmentation and regularization techniques.
- **Underfitting**: Addressed by using a sufficiently complex model and ensuring adequate feature representation.

## 4. Integration with APIs

### OpenAI API

**Purpose**: The OpenAI API processes the text output from the machine learning model, ensuring that translations are contextually accurate and coherent.

**Usage**:

- **Text Processing**: The API is called during the text translation phase to refine and enhance the output.
- **Example**:
  ```python
  response = openai.Completion.create(
      engine="text-davinci-003",
      prompt="Translate the following ASL signs to text:",
      input=data
  )
  ```

### ElevenLabs API

**Role**: The ElevenLabs API converts the text output into speech, providing an auditory translation of the ASL gestures.

**Usage**:

- **Text-to-Speech Conversion**: The API generates speech output from the translated text, making communication audible.
- **Example**:
  ```python
  speech = elevenlabs.Speech.create(
      text="Hello, how can I help you?",
      voice="Joanna"
  )
  ```

## 5. UI/UX Design

### User Interface

The user interface of the Sign Language Translator is designed to be straightforward and accessible, catering to users of all technical abilities. Key elements include:

- **Webcam View**: Displays the real-time video feed of the user signing in ASL, allowing immediate feedback.
- **Text Output Section**: Prominently shows the translated text, making it easy for users to read the output.
- **Audio Output Button**: Provides a simple button to play the speech output, ensuring that the translation can be heard as well as seen.

### User Experience

- **Intuitive Navigation**: The application features a streamlined interface, reducing the learning curve for new users.
- **Responsive Design**: The interface is optimized for both desktop and mobile devices, ensuring a consistent experience across different platforms.

## 6. Future Improvements

Looking ahead, the Sign Language Translator project plans to introduce several enhancements:

- **Support for Multiple Sign Languages**: The system will be expanded to include translations for other sign languages such as British Sign Language (BSL), Indian Sign Language (ISL), International Sign Language (ISL), and many others.
- **Enhanced Model Accuracy**: By incorporating larger datasets and utilizing advanced algorithms, the accuracy of the translations will be improved.
- **Offline Mode**: An offline version of the application will be developed, allowing users to access translations without an internet connection, increasing its accessibility.
- **Support of Multiple Spoken Languages**: The system will be expanded to include multiple languages other than just English to ensure inclusivity and help a global audience.

## Code Explanations

#### Part – 1: Machine Learning and Model Training

- **collect_images.py**:
Let me walk you through our data collection process. In collect_images.py, we utilize OpenCV to access the webcam feed. The script creates a sophisticated image collection system that captures 500 images for each of the 26 sign language classes - covering all letters A through Z. When you run the script, it first creates a structured data directory. What's unique about our approach is the real-time frame capture system - it waits for you to position your hand correctly, then automatically captures frames at optimal intervals. We've implemented a visual feedback system that shows you the current capture count and remaining images, making the data collection process user-friendly and efficient.
- **augment_data.py**:
To build a robust model, our augment_data.py script applies advanced augmentation techniques to each image, creating five variations through random rotation, shifting, zooming, brightness adjustment, and flipping. This enhances the dataset’s diversity and multiplies our dataset size by 5, improving the model’s performance with different angles and lighting conditions.
- **create_Dataset.py**:
The core of our feature extraction lies in create_Dataset.py. We leverage MediaPipe's hand tracking technology to identify 21 crucial hand landmarks - from the wrist to fingertips. Each landmark provides x, y, and z coordinates. To ensure consistency, we normalize these coordinates relative to the wrist position. The script processes these coordinates into a 63-dimensional feature vector for each image. We then package this data into a pickle file, creating a structured dataset that includes both features and their corresponding labels. This preprocessing step is crucial for achieving high accuracy in our final model.
- **train_classifier.py**:
Our train_classifier.py script uses a Random Forest Classifier, splitting data 80-20 for training and testing. It includes hyperparameter tuning and cross-validation, resulting in a model with over 98% accuracy, effective for real-world sign language translation.
NOW MOVING ON TO THE FUNCTIONS.

#### Part – 2: Functions
- **speech_to_text.py**:
For voice input processing, we implemented speech_to_text.py using the SpeechRecognition library. The script activates your microphone, adjusts for ambient noise, and converts spoken words into text. It uses Google's speech recognition API for accurate transcription, with built-in error handling for unclear audio or connection issues.
- **text_fix.py**:
Our text_fix.py script is crucial for grammar correction. Using OpenAI's API, it processes the raw text input to ensure proper sentence structure. What makes this unique is our custom prompt engineering that maintains the original meaning while fixing spacing and punctuation issues, especially important for sign language translations where words might be spaced irregularly.
- **video_module.py**:
The core real-time processing happens in video_module.py. This script captures webcam feed and processes it through our trained model. It implements:
•	Real-time landmark detection using MediaPipe
•	Character prediction with confidence scores
•	A stabilization system with a 2-second delay to prevent flickering
•	Live visualization of detected signs and the forming sentence
The system maintains high accuracy while providing immediate visual feedback.
- **voice.py**:
Finally, voice.py handles text-to-speech conversion using the ElevenLabs API. It processes our translated text into natural-sounding speech, with customizable voice settings for stability and clarity. The script includes automatic file cleanup after playback, making it memory efficient.
- **text_to_sign.py**:
For text-to-sign conversion, text_to_sign.py uses a dictionary mapping each letter to its sign language image. It processes text character by character, converting letters into sign representations. The script includes base64 encoding for efficient image handling and supports spaces between words, ensuring accurate American Sign Language gestures.

#### Part – 3: User Interface

- **app.py**:
Our Flask application serves as the backend, handling all core functionalities. It manages real-time video processing with OpenCV and MediaPipe, implements our trained model for sign detection, and coordinates all API interactions. Key features include:
•	Real-time sign language detection with stability checks
•	Sentence formation with a 2-second stabilization delay
•	Integration with speech-to-text and text-to-speech services
•	RESTful API endpoints for all conversion features
- **index.html**:
The frontend interface is clean and intuitive, featuring:
•	Live video feed display
•	Record and Stop controls
•	Real-time prediction display
•	Text output area
•	Text-to-sign and speech-to-sign conversion options
The layout prioritizes user experience with clear visual feedback.
- **main.js**:
The JavaScript handles all client-side interactions:
•	Camera stream management
•	Real-time API communication
•	Sign language display timing
•	Speech recording controls
It includes error handling and smooth transitions between different conversion modes.


## 7. Conclusion

The Sign Language Translator is a pioneering project that significantly contributes to breaking down communication barriers between sign language users and non-users. By transforming ASL gestures into text and speech, it promotes inclusivity and facilitates better interaction in diverse settings. This documentation provides a thorough guide for both users and developers, detailing every aspect of the project's installation, usage, and technical framework, along with plans for future developments.

## 8. Appendices

### Glossary

- **ASL**: American Sign Language, a visual language used primarily in the United States and Canada, similar to International Sign Language, which is used worldwide.
- **MediaPipe**: A framework developed by Google for building multimodal perception pipelines.
- **scikit-learn**: A machine learning library in Python, providing simple and efficient tools for data mining and data analysis.

### References

- **MediaPipe Documentation**: [https://mediapipe.dev/](https://mediapipe.dev/)
- **scikit-learn Documentation**: [https://scikit-learn.org/stable/](https://scikit-learn.org/stable/)
- **OpenAI API**: [https://openai.com/api/](https://openai.com/api/)
- **ElevenLabs API**: [https://elevenlabs.io/api/](https://elevenlabs.io/api/)

### Code Snippets

- **MediaPipe Integration**:
  ```python
  import mediapipe as mp
  hands = mp.solutions.hands.Hands()
  ```
- **scikit-learn Model Training**:
  ```python
  from sklearn.ensemble import

