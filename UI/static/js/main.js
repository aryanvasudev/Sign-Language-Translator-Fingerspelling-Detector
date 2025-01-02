let stream = null;
let recording = false;

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

// Keep these functions for future implementation
function convertText() {
    // Future implementation for text conversion
}

function convertSpeech() {
    // Future implementation for speech conversion
}

document.addEventListener('DOMContentLoaded', () => {
    // Any initialization code can go here
});
