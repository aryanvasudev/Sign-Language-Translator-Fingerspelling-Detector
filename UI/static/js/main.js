document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const recordBtn = document.getElementById('record');
    const stopBtn = document.getElementById('stop');
    const predictionBox = document.getElementById('prediction');

    let stream = null;
    let recording = false;

    recordBtn.addEventListener('click', async () => {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        recording = true;
        // Add recording logic
    });

    stopBtn.addEventListener('click', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            recording = false;
        }
    });

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
            predictionBox.textContent = result.prediction;
        } catch (error) {
            console.error('Error:', error);
        }
    }
});
