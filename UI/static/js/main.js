let stream = null;
let recording = false;
let currentImageIndex = 0;
let imagesData = [];
let imageInterval;
let audioRecording = false;
let audioFilename = '';

function startRecording() {
    recording = true;
    fetch('/start_recording', {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(videoStream => {
                    stream = videoStream;
                    document.getElementById('video').srcObject = stream;
                })
                .catch(error => console.error('Error accessing camera:', error));
        }
    });
}

function stopRecording() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        document.getElementById('video').srcObject = null;
    }
    recording = false;
    fetch('/stop_recording', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output-box').textContent = data.meaningful_sentence;
    });
}

setInterval(() => {
    if (recording) {
        fetch('/get_current_prediction')
            .then(response => response.json())
            .then(data => {
                document.getElementById('prediction-box').textContent = data.prediction;
            });
    }
}, 1000);

function displayNextImage() {
    const signDisplay = document.getElementById('sign-display');
    if (currentImageIndex < imagesData.length) {
        const imageData = imagesData[currentImageIndex];
        if (imageData.image) {
            signDisplay.innerHTML = `<img src="data:image/png;base64,${imageData.image}" alt="${imageData.character}" style="max-width: 100%; max-height: 100%;">`;
        } else {
            signDisplay.innerHTML = '<p>SPACE</p>';
        }
        currentImageIndex++;
    } else {
        clearInterval(imageInterval);
        currentImageIndex = 0;
    }
}

function convertText() {
    const textInput = document.getElementById('text-input').value;
    if (!textInput) {
        alert('No input found! Please enter some text.');
        return;
    }
    
    fetch('/convert_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: textInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            alert(data.message);
        } else {
            clearInterval(imageInterval);
            imagesData = data.images;
            currentImageIndex = 0;
            imageInterval = setInterval(displayNextImage, 1000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error converting text to sign language');
    });
}

function convertSpeech() {
    if (!audioRecording) {
        audioRecording = true;
        fetch('/start_speech_recording', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                audioFilename = data.filename;
            } else {
                alert('Error starting speech recording');
                audioRecording = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            audioRecording = false;
        });
    }
}

function stopConversion() {
    if (audioRecording) {
        audioRecording = false;
        fetch('/stop_speech_recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: audioFilename })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                clearInterval(imageInterval);
                imagesData = data.images;
                currentImageIndex = 0;
                imageInterval = setInterval(displayNextImage, 1000);
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error converting speech to sign language');
        });
    }
}

function speakText() {
    fetch('/speak_text', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            console.error('Error playing audio:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

async function sendPredictionRequest(data) {
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        document.getElementById('prediction-box').textContent = result.prediction;
    } catch (error) {
        console.error('Error:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialization code (if needed)
});
