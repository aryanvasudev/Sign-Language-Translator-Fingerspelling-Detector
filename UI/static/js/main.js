let stream = null;
let recording = false;
let currentImageIndex = 0;
let imagesData = [];
let imageInterval;
let audioRecording = false;
let audioFilename = '';
let speechInterval;

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

function convertSpeech() {
    if (!audioRecording) {
        audioRecording = true;
        document.getElementById('text-input').value = '';
        
        fetch('/convert_speech_to_sign', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('text-input').value = data.text;
                imagesData = data.images;
                currentImageIndex = 0;
                clearInterval(imageInterval);
                imageInterval = setInterval(displayNextImage, 1000);
            } else {
                console.error('Error:', data.message);
                alert('Error converting speech to sign language');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error during speech conversion');
        })
        .finally(() => {
            audioRecording = false;
        });
    }
}

function displayNextImage() {
    const signDisplay = document.getElementById('sign-display');
    if (currentImageIndex < imagesData.length) {
        const imageData = imagesData[currentImageIndex];
        if (imageData.image) {
            signDisplay.innerHTML = `<img src="data:image/png;base64,${imageData.image}" alt="${imageData.character}">`;
        } else {
            signDisplay.innerHTML = '<p>SPACE</p>';
        }
        currentImageIndex++;
    } else {
        clearInterval(imageInterval);
        currentImageIndex = 0;
    }
}


document.addEventListener('DOMContentLoaded', () => {
// add more event listeners here as needed if you are contributing to this project
});
