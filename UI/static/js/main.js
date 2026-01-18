/**
 * SignBridge — ASL Translator
 * Main JavaScript Controller
 *
 * Handles all client-side interactions including:
 * - Recording control for sign-to-text translation
 * - Text-to-sign conversion with animated display
 * - Speech-to-sign conversion
 * - UI state management, toasts, and loading states
 */

// =============================================================================
// STATE MANAGEMENT
// =============================================================================

let recording = false;
let currentImageIndex = 0;
let imagesData = [];
let imageInterval = null;
let speechRecording = false;

// =============================================================================
// DOM ELEMENTS (cached for performance)
// =============================================================================

const elements = {
    get loadingOverlay() { return document.getElementById('loading-overlay'); },
    get toast() { return document.getElementById('toast'); },
    get toastMessage() { return document.getElementById('toast-message'); },
    get recordBtn() { return document.getElementById('record-btn'); },
    get stopBtn() { return document.getElementById('stop-btn'); },
    get speakBtn() { return document.getElementById('speak-btn'); },
    get convertTextBtn() { return document.getElementById('convert-text-btn'); },
    get convertSpeechBtn() { return document.getElementById('convert-speech-btn'); },
    get predictionBox() { return document.getElementById('prediction-box'); },
    get outputBox() { return document.getElementById('output-box'); },
    get textInput() { return document.getElementById('text-input'); },
    get charCount() { return document.getElementById('char-count'); },
    get signDisplay() { return document.getElementById('sign-display'); },
    get recordingIndicator() { return document.getElementById('recording-indicator'); },
    get progressBar() { return document.getElementById('progress-bar'); },
    get signProgress() { return document.getElementById('sign-progress'); }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Show the loading overlay with animation
 */
function showLoading() {
    const overlay = elements.loadingOverlay;
    if (overlay) {
        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');
    }
}

/**
 * Hide the loading overlay
 */
function hideLoading() {
    const overlay = elements.loadingOverlay;
    if (overlay) {
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');
    }
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - 'error', 'success', or 'info'
 * @param {number} duration - How long to show the toast (ms)
 */
function showToast(message, type = 'error', duration = 5000) {
    const toast = elements.toast;
    const toastMessage = elements.toastMessage;

    if (toast && toastMessage) {
        toastMessage.textContent = message;
        toast.className = `toast toast-${type} show`;

        // Auto-hide after duration
        setTimeout(() => {
            hideToast();
        }, duration);
    }
}

/**
 * Hide the toast notification
 */
function hideToast() {
    const toast = elements.toast;
    if (toast) {
        toast.classList.remove('show');
    }
}

/**
 * Disable a button and show loading state
 * @param {string} buttonId - The button element ID
 */
function setButtonLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.classList.add('loading');
    }
}

/**
 * Re-enable a button and restore original state
 * @param {string} buttonId - The button element ID
 */
function resetButton(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

/**
 * Make a fetch request with error handling
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<object>} - The JSON response
 */
async function fetchWithErrorHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Network error. Please check your connection.');
        }
        throw error;
    }
}

/**
 * Update the progress bar
 * @param {number} current - Current position
 * @param {number} total - Total items
 */
function updateProgressBar(current, total) {
    const progressBar = elements.progressBar;
    const signProgress = elements.signProgress;

    if (progressBar && signProgress) {
        const percentage = total > 0 ? (current / total) * 100 : 0;
        progressBar.style.width = `${percentage}%`;

        // Show/hide progress bar container
        if (total > 0) {
            signProgress.classList.add('active');
        } else {
            signProgress.classList.remove('active');
        }
    }
}

// =============================================================================
// SIGN TO TEXT FUNCTIONS
// =============================================================================

/**
 * Show recording indicator
 */
function showRecordingIndicator() {
    const indicator = elements.recordingIndicator;
    if (indicator) {
        indicator.classList.add('active');
    }
}

/**
 * Hide recording indicator
 */
function hideRecordingIndicator() {
    const indicator = elements.recordingIndicator;
    if (indicator) {
        indicator.classList.remove('active');
    }
}

/**
 * Start recording sign language gestures
 */
async function startRecording() {
    if (recording) {
        showToast('Already recording!', 'info');
        return;
    }

    try {
        setButtonLoading('record-btn');

        const data = await fetchWithErrorHandling('/start_recording', {
            method: 'POST'
        });

        if (data.status === 'success') {
            recording = true;
            showToast('Recording started! Show your signs to the camera.', 'success', 3000);

            // Update UI to show recording state
            elements.recordBtn?.classList.add('recording');
            showRecordingIndicator();

            if (elements.predictionBox) {
                elements.predictionBox.textContent = '—';
            }
            if (elements.outputBox) {
                elements.outputBox.textContent = 'Your translated text will appear here...';
            }
        } else {
            showToast(data.message || 'Failed to start recording', 'error');
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        showToast(error.message || 'Failed to start recording', 'error');
    } finally {
        resetButton('record-btn');
    }
}

/**
 * Stop recording and process the detected sentence
 */
async function stopRecording() {
    if (!recording) {
        showToast('Not currently recording', 'info');
        return;
    }

    try {
        setButtonLoading('stop-btn');
        showLoading();

        const data = await fetchWithErrorHandling('/stop_recording', {
            method: 'POST'
        });

        recording = false;
        elements.recordBtn?.classList.remove('recording');
        hideRecordingIndicator();

        if (data.status === 'success') {
            const outputBox = elements.outputBox;

            if (data.meaningful_sentence) {
                if (outputBox) outputBox.textContent = data.meaningful_sentence;
                showToast('Recording processed successfully!', 'success', 3000);
            } else if (data.raw_text) {
                if (outputBox) outputBox.textContent = data.raw_text;
                showToast('No text correction available', 'info');
            } else {
                if (outputBox) outputBox.textContent = 'No signs detected. Try again.';
                showToast('No signs were detected', 'info');
            }
        } else {
            showToast(data.message || 'Failed to process recording', 'error');
        }
    } catch (error) {
        console.error('Error stopping recording:', error);
        showToast(error.message || 'Failed to stop recording', 'error');
        recording = false;
        hideRecordingIndicator();
    } finally {
        resetButton('stop-btn');
        hideLoading();
    }
}

/**
 * Update the prediction display periodically while recording
 */
function updatePrediction() {
    if (!recording) return;

    fetch('/get_current_prediction')
        .then(response => response.json())
        .then(data => {
            const predictionBox = elements.predictionBox;
            if (predictionBox && data.prediction) {
                predictionBox.textContent = data.prediction;
                predictionBox.classList.add('pulse');
                setTimeout(() => predictionBox.classList.remove('pulse'), 300);
            }
        })
        .catch(error => {
            console.error('Error fetching prediction:', error);
        });
}

// Poll for predictions every second while recording
setInterval(updatePrediction, 1000);

/**
 * Speak the translated text using text-to-speech
 */
async function speakText() {
    const outputBox = elements.outputBox;
    const text = outputBox?.textContent?.trim();

    if (!text || text === 'Your translated text will appear here...' || text === 'No signs detected. Try again.') {
        showToast('No text to speak. Record some signs first.', 'info');
        return;
    }

    try {
        setButtonLoading('speak-btn');

        const data = await fetchWithErrorHandling('/speak_text', {
            method: 'POST'
        });

        if (data.status === 'success') {
            showToast('Audio played successfully', 'success', 2000);
        } else {
            showToast(data.message || 'Failed to play audio', 'error');
        }
    } catch (error) {
        console.error('Error speaking text:', error);
        showToast(error.message || 'Failed to play audio', 'error');
    } finally {
        resetButton('speak-btn');
    }
}

// =============================================================================
// TEXT TO SIGN FUNCTIONS
// =============================================================================

/**
 * Reset sign display to placeholder state
 */
function resetSignDisplay() {
    const signDisplay = elements.signDisplay;
    if (signDisplay) {
        signDisplay.innerHTML = `
            <div class="sign-placeholder">
                <svg viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M40 10C55 15 65 30 60 50C55 70 25 75 15 55C5 35 15 15 35 10C38 9 38 9 40 10Z" opacity="0.3"/>
                    <circle cx="35" cy="40" r="4" fill="currentColor" opacity="0.3"/>
                </svg>
                <p>Sign gestures will appear here</p>
            </div>
        `;
    }
    updateProgressBar(0, 0);
}

/**
 * Convert text input to sign language images
 */
async function convertText() {
    const textInput = elements.textInput;
    const text = textInput?.value?.trim();

    if (!text) {
        showToast('Please enter some text to convert', 'info');
        return;
    }

    if (text.length > 500) {
        showToast('Text is too long. Maximum 500 characters allowed.', 'error');
        return;
    }

    try {
        setButtonLoading('convert-text-btn');
        showLoading();

        const data = await fetchWithErrorHandling('/convert_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        if (data.status === 'success') {
            // Stop any existing animation
            if (imageInterval) {
                clearInterval(imageInterval);
            }

            imagesData = data.images;
            currentImageIndex = 0;

            if (imagesData.length > 0) {
                showToast(`Converting ${imagesData.length} characters to sign language`, 'success', 2000);
                updateProgressBar(0, imagesData.length);
                imageInterval = setInterval(displayNextImage, 1000);
            } else {
                showToast('No valid characters to convert', 'info');
                resetSignDisplay();
            }
        } else {
            showToast(data.message || 'Failed to convert text', 'error');
        }
    } catch (error) {
        console.error('Error converting text:', error);
        showToast(error.message || 'Failed to convert text', 'error');
    } finally {
        resetButton('convert-text-btn');
        hideLoading();
    }
}

/**
 * Convert speech to sign language
 */
async function convertSpeech() {
    if (speechRecording) {
        showToast('Already recording speech', 'info');
        return;
    }

    try {
        speechRecording = true;
        setButtonLoading('convert-speech-btn');
        showLoading();

        // Clear the text input to show we're listening
        if (elements.textInput) {
            elements.textInput.value = '';
            updateCharCount();
        }

        const data = await fetchWithErrorHandling('/convert_speech_to_sign', {
            method: 'POST'
        });

        if (data.status === 'success') {
            // Show recognized text in the input
            if (elements.textInput) {
                elements.textInput.value = data.text;
                updateCharCount();
            }

            // Start sign animation
            if (imageInterval) {
                clearInterval(imageInterval);
            }

            imagesData = data.images;
            currentImageIndex = 0;

            if (imagesData.length > 0) {
                showToast(`Recognized: "${data.text}"`, 'success', 3000);
                updateProgressBar(0, imagesData.length);
                imageInterval = setInterval(displayNextImage, 1000);
            }
        } else {
            showToast(data.message || 'Could not understand speech', 'error');
        }
    } catch (error) {
        console.error('Error converting speech:', error);
        showToast(error.message || 'Speech conversion failed', 'error');
    } finally {
        speechRecording = false;
        resetButton('convert-speech-btn');
        hideLoading();
    }
}

/**
 * Display the next sign language image in the sequence
 */
function displayNextImage() {
    const signDisplay = elements.signDisplay;

    if (currentImageIndex < imagesData.length) {
        const imageData = imagesData[currentImageIndex];

        // Update progress bar
        updateProgressBar(currentImageIndex + 1, imagesData.length);

        if (imageData.image) {
            signDisplay.innerHTML = `
                <div class="sign-content">
                    <img src="data:image/png;base64,${imageData.image}"
                         alt="Sign language gesture for letter ${imageData.character}"
                         class="sign-image">
                    <span class="sign-letter">${imageData.character}</span>
                </div>
            `;
        } else {
            // Space character
            signDisplay.innerHTML = `
                <div class="sign-content space-indicator">
                    <div class="space-visual">
                        <svg viewBox="0 0 60 20" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M5 10h50" stroke-dasharray="4 4"/>
                        </svg>
                    </div>
                    <span class="sign-letter">SPACE</span>
                </div>
            `;
        }

        // Add animation class
        signDisplay.classList.add('transitioning');
        setTimeout(() => signDisplay.classList.remove('transitioning'), 300);

        currentImageIndex++;
    } else {
        // Animation complete
        clearInterval(imageInterval);
        imageInterval = null;
        currentImageIndex = 0;

        // Show completion message
        setTimeout(() => {
            signDisplay.innerHTML = `
                <div class="sign-complete">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22,4 12,14.01 9,11.01"/>
                    </svg>
                    <p>Conversion complete!</p>
                    <span>Enter new text to continue</span>
                </div>
            `;
            updateProgressBar(0, 0);
        }, 500);
    }
}

// =============================================================================
// CHARACTER COUNT
// =============================================================================

/**
 * Update the character count display
 */
function updateCharCount() {
    const textInput = elements.textInput;
    const charCount = elements.charCount;

    if (textInput && charCount) {
        const length = textInput.value.length;
        charCount.textContent = length;

        // Visual feedback when approaching limit
        const counter = charCount.parentElement;
        if (counter) {
            counter.classList.toggle('warning', length > 450);
            counter.classList.toggle('danger', length >= 500);
        }
    }
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

/**
 * Handle keyboard shortcuts
 * @param {KeyboardEvent} event
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd+Enter to convert text
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.id === 'text-input') {
            event.preventDefault();
            convertText();
        }
    }

    // Escape to stop recording
    if (event.key === 'Escape' && recording) {
        stopRecording();
    }

    // Space to start recording when focused on record button
    if (event.key === ' ' && document.activeElement?.id === 'record-btn' && !recording) {
        event.preventDefault();
        startRecording();
    }
}

// =============================================================================
// ACCESSIBILITY
// =============================================================================

/**
 * Announce to screen readers
 * @param {string} message - Message to announce
 */
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);

    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// =============================================================================
// VIDEO FEED MANAGEMENT
// =============================================================================

let videoFeedRetryCount = 0;
const MAX_VIDEO_RETRIES = 10;
const VIDEO_RETRY_DELAY = 3000;
let videoFeedCheckInterval = null;

/**
 * Initialize video feed with error handling and auto-reconnect
 */
function initializeVideoFeed() {
    const cameraFeed = document.getElementById('camera-feed');
    if (!cameraFeed) return;

    // Set initial source
    refreshVideoFeed();

    // Handle image load errors
    cameraFeed.onerror = function() {
        console.error('Video feed error, attempting reconnect...');
        handleVideoFeedError();
    };

    // Check if video feed is stale (no updates)
    startVideoFeedMonitor();
}

/**
 * Refresh the video feed by resetting the src
 */
function refreshVideoFeed() {
    const cameraFeed = document.getElementById('camera-feed');
    if (!cameraFeed) return;

    // Add timestamp to force reload
    const timestamp = new Date().getTime();
    const baseUrl = '/video_feed';
    cameraFeed.src = `${baseUrl}?t=${timestamp}`;
    console.log('Video feed refreshed');
}

/**
 * Handle video feed errors with retry logic
 */
function handleVideoFeedError() {
    videoFeedRetryCount++;

    if (videoFeedRetryCount <= MAX_VIDEO_RETRIES) {
        console.log(`Retrying video feed (${videoFeedRetryCount}/${MAX_VIDEO_RETRIES})...`);
        showToast(`Camera reconnecting... (${videoFeedRetryCount}/${MAX_VIDEO_RETRIES})`, 'info', 2000);

        setTimeout(() => {
            refreshVideoFeed();
        }, VIDEO_RETRY_DELAY);
    } else {
        console.error('Max video feed retries reached');
        showToast('Camera connection lost. Please refresh the page.', 'error', 10000);
    }
}

/**
 * Monitor video feed for stale frames
 */
function startVideoFeedMonitor() {
    const cameraFeed = document.getElementById('camera-feed');
    if (!cameraFeed) return;

    let lastLoadTime = Date.now();

    // Track successful loads
    cameraFeed.onload = function() {
        lastLoadTime = Date.now();
        videoFeedRetryCount = 0; // Reset retry count on successful load
    };

    // Periodically check if feed is stale (no load events for 10 seconds)
    if (videoFeedCheckInterval) {
        clearInterval(videoFeedCheckInterval);
    }

    videoFeedCheckInterval = setInterval(() => {
        const timeSinceLastLoad = Date.now() - lastLoadTime;

        // If no load event for 10 seconds and we're not already retrying
        if (timeSinceLastLoad > 10000 && videoFeedRetryCount === 0) {
            console.warn('Video feed appears stale, refreshing...');
            refreshVideoFeed();
        }
    }, 5000);
}

/**
 * Clean up video feed monitoring
 */
function cleanupVideoFeed() {
    if (videoFeedCheckInterval) {
        clearInterval(videoFeedCheckInterval);
        videoFeedCheckInterval = null;
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Set up character count listener
    const textInput = elements.textInput;
    if (textInput) {
        textInput.addEventListener('input', updateCharCount);

        // Auto-resize textarea (optional enhancement)
        textInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }

    // Set up keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Initialize character count
    updateCharCount();

    // Initialize progress bar
    updateProgressBar(0, 0);

    // Initialize video feed with auto-reconnect
    initializeVideoFeed();

    // Add focus styles for keyboard navigation
    document.body.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-nav');
        }
    });

    document.body.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-nav');
    });

    // Clean up on page unload
    window.addEventListener('beforeunload', cleanupVideoFeed);

    console.log('SignBridge initialized successfully');
});

// =============================================================================
// EXPOSE FUNCTIONS GLOBALLY (for onclick handlers)
// =============================================================================

window.startRecording = startRecording;
window.stopRecording = stopRecording;
window.speakText = speakText;
window.convertText = convertText;
window.convertSpeech = convertSpeech;
window.hideToast = hideToast;
window.refreshVideoFeed = refreshVideoFeed;
