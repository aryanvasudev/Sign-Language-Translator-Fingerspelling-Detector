"""
Pytest Configuration and Fixtures

This module contains pytest fixtures used across all test modules.
"""

import pytest
import sys
import os

# Add the UI directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI'))


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Set environment variables for testing
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    os.environ.setdefault('ELEVENLABS_API_KEY', 'test-key')
    os.environ.setdefault('ELEVENLABS_VOICE_ID', 'test-voice-id')

    # Import after setting env vars to avoid validation errors
    from app import app as flask_app

    flask_app.config.update({
        'TESTING': True,
    })

    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def mock_model(mocker):
    """Mock the ML model for testing."""
    mock = mocker.MagicMock()
    mock.predict.return_value = [0]  # Predict 'a'
    mock.predict_proba.return_value = [[0.95] + [0.002] * 25]
    return mock


@pytest.fixture
def sample_hand_landmarks(mocker):
    """Create mock hand landmarks for testing."""
    # Create 21 mock landmarks
    landmarks = []
    for i in range(21):
        landmark = mocker.MagicMock()
        landmark.x = 0.5 + (i * 0.01)
        landmark.y = 0.5 + (i * 0.01)
        landmarks.append(landmark)

    mock_hand = mocker.MagicMock()
    mock_hand.landmark = landmarks
    return mock_hand
