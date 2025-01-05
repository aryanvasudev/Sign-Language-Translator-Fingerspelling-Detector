# **Sign Language Translator: Fingerspelling Detector**

<p align="center">
    <b>Project By Jashanpreet Singh and Aryan Vasudev -- Team CodeCrushers</b>
</p>

<p align="center">
  <img src="Assets/CodeCrushers.png" alt="Sign Language Translator Logo" width="200"/>
</p>

<p align="center">
  <b>An innovative AI-powered tool designed to bridge communication gaps by translating American Sign Language (ASL) fingerspelling into text, converting text back into fingerspelling animations, and providing an integrated speech system for audible output. This project leverages state-of-the-art machine learning and computer vision technologies to enable real-time, seamless, and accessible communication for all users.</b>
</p>

## 📑 **Table of Contents**

- [Features](#-features)  
- [Demo](#-demo)  
- [Installation](#-installation)  
- [Usage](#-usage)  
- [Project Structure](#-project-structure)  
- [Flow Charts](#-flow-charts)  
- [Technical Overview](#-technical-overview)  
- [Glossary](#-glossary)  
- [Future Plans](#-future-plans)  
- [User Feedback](#-user-feedback)  
- [Contributing](#-contributing)  
- [License](#-license)  

## 🌟 **Features**

- 🖐️ **Real-time ASL Fingerspelling Detection**: Detects and translates ASL fingerspelling gestures into text in real-time.  
- 🔡 **Text-to-Sign Conversion**: Converts input text into fingerspelling animations, bridging communication gaps for non-ASL speakers.  
- 🔊 **Integrated Speech System**: Converts text to speech, making the communication output audible.  
- 📂 **Lightweight and User-Friendly**: Optimized for accessibility and ease of use.  

## 🎥 **Demo**

A live demo showcasing the project's features will be available soon. Stay tuned! The link to the YouTube video will be added here: [Demo Link](#)

## 🚀 **Installation**

1. Clone the repository:

   ```bash
   git clone https://github.com/JashanMaan28/Sign-Language-Translator-Fingerspelling-Detector.git
   ```

2. Navigate to the project directory:  
   ```bash
   cd Sign-Language-Translator-Fingerspelling-Detector
   ```

3. Install the required packages:  
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ **Usage**

Navigate to the directory:

```bash
cd UI
```  

To start the Sign Language Translator, run:

```bash
python app.py
```  

## 📂 **Project Structure**

```plaintext
--- Folder Structure ---
.env
.env.example
.gitignore
[augmented-data]
    ├── [0]
    ├── [Add 0 to 26 folders only if you are training again or just leave this as the data has been already trained into the model.]
CODE_OF_CONDUCT.md
[datasets]
    ├── dataset.pickle
    └── [letter_images]
        ├── A.png
        ├── B.png
        ├── C.png
        ├── D.png
        ├── E.png
        ├── F.png
        ├── G.png
        ├── H.png
        ├── I.png
        ├── J.png
        ├── K.png
        ├── L.png
        ├── M.png
        ├── N.png
        ├── O.png
        ├── P.png
        ├── Q.png
        ├── R.png
        ├── S.png
        ├── T.png
        ├── U.png
        ├── V.png
        ├── W.png
        ├── X.png
        ├── Y.png
        └── Z.png
LICENSE
[logo]
    └── CodeCrushers.png
[model]
    └── model.p
[model-creation]
    ├── augment_data.py
    ├── collect_images.py
    ├── create_Dataset.py
    ├── model_test.py
    └── train_classifier.py
README.md
requirements.txt
[UI]
    ├── app.py
    ├── [functions]
        ├── speech_to_text.py
        ├── text_fix.py
        ├── text_to_sign.py
        ├── video_module.py
        └── voice.py
    ├── [static]
        ├── [css]
            └── style.css
        └── [js]
            └── main.js
    └── [templates]
        └── index.html
```

### Features:
- **Sign to Text**: Translates ASL fingerspelling gestures into readable text in real-time.
- **Text to Sign**: Converts input text into animated fingerspelling gestures, enhancing communication for non-ASL speakers.
- **Speech Output**: Generates audible speech from text, providing an additional layer of accessibility.

To know more about these features, watch the [Demo Video](#).

### Troubleshooting:
If you encounter issues, ensure:
- Python and required libraries are installed correctly.
- This Program was built on Python version 11.6
- Your camera permissions are enabled for gesture detection.

## 📊 **Flow Charts**

Flow charts explaining the system's architecture and process will be added here soon. This will include:

NOTE - Open the Flowchart in a New tab to view it correctly.

<p align="center">
  <img src="Assets/Sign_Language_Translate_FlowChart.svg" alt="Sign Language Translator Logo"/>
</p>


## 🧑‍💻 **Technical Overview**

This project utilizes a combination of machine learning and computer vision technologies to deliver seamless functionality:
- **OpenCV**: Used for video and image processing to detect fingerspelling gestures.
- **MediaPipe**: Powers the hand-tracking and gesture recognition modules.
- **Flask**: Enables the backend logic and serves the user interface.
- **Pickle**: Used for saving and loading trained machine learning models.

Other tools and libraries are also integrated to optimize performance and usability.

## 📖 **Glossary**

- **ASL**: American Sign Language, a visual language used primarily by the Deaf community in the United States.
- **Fingerspelling**: A method of spelling words using hand movements to represent each letter.
- **Machine Learning**: A subset of artificial intelligence enabling systems to learn and improve from experience.
- **MediaPipe**: A framework for building machine learning pipelines for live and streaming media.
- **OpenCV**: Open Source Computer Vision Library for real-time image and video processing.

## 🔮 **Future Plans**

We aim to:
- Add support for multilingual sign languages.
- Add support for multilingual spoken languages.
- Enhance gesture detection accuracy.

## 📢 **User Feedback**

Your feedback is invaluable! If you encounter issues, have suggestions, or want to share your experience:
- Open an issue on the GitHub repository.
- Contact us directly at [jmaan1337@gmail.com] or [aryanvasudev28@gmail.com].

We look forward to hearing from you!

## 🤝 **Contributing**

Contributions are welcome! Here's how to contribute:  

NOTE - Please Contribute after January 10, 2025 or your Contribution may not be considered

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature/YourFeature`).  
3. Commit your changes (`git commit -m 'Add YourFeature'`).  
4. Push to the branch (`git push origin feature/YourFeature`).  
5. Open a Pull Request.  

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/JashanMaan28">Jashanpreet Singh</a> and <a href="https://github.com/aryanvasudev">Aryan Vasudev</a>. Team CodeCrushers
</p>
