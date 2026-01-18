"""
Tests for Flask Application Routes

This module tests the Flask routes and API endpoints.
"""

import pytest
import json


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'model_loaded' in data


class TestIndexRoute:
    """Tests for the main index page."""

    def test_index_returns_html(self, client):
        """Test that index page returns HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Sign Language Translator' in response.data


class TestRecordingEndpoints:
    """Tests for the recording start/stop endpoints."""

    def test_start_recording_returns_success(self, client):
        """Test that start recording returns success."""
        response = client.post('/start_recording')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_stop_recording_returns_success(self, client):
        """Test that stop recording returns success."""
        # First start recording
        client.post('/start_recording')

        response = client.post('/stop_recording')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'raw_text' in data
        assert 'meaningful_sentence' in data

    def test_get_current_prediction(self, client):
        """Test that current prediction endpoint works."""
        response = client.get('/get_current_prediction')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'prediction' in data


class TestConvertTextEndpoint:
    """Tests for the /convert_text endpoint."""

    def test_convert_text_with_valid_input(self, client):
        """Test text conversion with valid input."""
        response = client.post(
            '/convert_text',
            json={'text': 'HELLO'},
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'images' in data
        assert len(data['images']) == 5  # H-E-L-L-O

    def test_convert_text_with_empty_input(self, client):
        """Test text conversion with empty input returns error."""
        response = client.post(
            '/convert_text',
            json={'text': ''},
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_convert_text_with_no_json(self, client):
        """Test text conversion without JSON returns error."""
        response = client.post('/convert_text')
        assert response.status_code == 400

    def test_convert_text_with_too_long_input(self, client):
        """Test text conversion with input exceeding max length."""
        long_text = 'A' * 501  # Exceeds 500 char limit
        response = client.post(
            '/convert_text',
            json={'text': long_text},
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'too long' in data['message'].lower()

    def test_convert_text_filters_non_letters(self, client):
        """Test that non-letter characters are filtered out."""
        response = client.post(
            '/convert_text',
            json={'text': 'H3LL0!'},  # Numbers and special chars
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        # Should only get H, L, L (3 letters)
        assert len(data['images']) == 3

    def test_convert_text_with_only_numbers(self, client):
        """Test text conversion with only numbers returns error."""
        response = client.post(
            '/convert_text',
            json={'text': '12345'},
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestSpeakTextEndpoint:
    """Tests for the /speak_text endpoint."""

    def test_speak_text_without_recording(self, client):
        """Test speak text when no recording has been made."""
        response = client.post('/speak_text')
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return error since no text to speak
        assert data['status'] == 'error'


class TestSignLanguageDetector:
    """Tests for the SignLanguageDetector class."""

    def test_detector_initialization(self):
        """Test that detector initializes with correct defaults."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI'))

        from app import SignLanguageDetector

        detector = SignLanguageDetector()

        assert detector.detected_sentence == []
        assert detector.is_recording is False
        assert detector.stable_char == ""

    def test_detector_start_recording(self):
        """Test starting recording mode."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI'))

        from app import SignLanguageDetector

        detector = SignLanguageDetector()
        detector.start_recording()

        assert detector.is_recording is True
        assert detector.detected_sentence == []

    def test_detector_stop_recording(self):
        """Test stopping recording mode."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI'))

        from app import SignLanguageDetector

        detector = SignLanguageDetector()
        detector.start_recording()
        detector.detected_sentence = ['A', 'B', 'C']

        raw_text, _ = detector.stop_recording()

        assert detector.is_recording is False
        assert raw_text == 'A B C'

    def test_detector_check_sign_stability(self):
        """Test sign stability checking."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI'))

        from app import SignLanguageDetector

        detector = SignLanguageDetector()

        # Should not be stable with just one prediction
        is_stable, prediction = detector.check_sign_stability('A')
        assert is_stable is False

        # Add more predictions
        for _ in range(4):
            is_stable, prediction = detector.check_sign_stability('A')

        # Should be stable after 5 identical predictions
        assert is_stable is True
        assert prediction == 'A'
