"""
Tests for Text to Sign Module

This module tests the text_to_sign conversion functionality.
"""

import pytest
import sys
import os

# Add the UI/functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'UI', 'functions'))


class TestTextToSignLanguage:
    """Tests for the text_to_sign_language function."""

    def test_empty_text_returns_empty_list(self):
        """Test that empty text returns empty list."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('')
        assert result == []

    def test_single_letter_conversion(self):
        """Test conversion of single letter."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('A')

        assert len(result) == 1
        assert result[0]['character'] == 'A'
        # Image should be present (base64 encoded) or None if file not found
        assert 'image' in result[0]

    def test_multiple_letters_conversion(self):
        """Test conversion of multiple letters."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('ABC')

        assert len(result) == 3
        assert result[0]['character'] == 'A'
        assert result[1]['character'] == 'B'
        assert result[2]['character'] == 'C'

    def test_lowercase_converted_to_uppercase(self):
        """Test that lowercase letters are converted to uppercase."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('abc')

        assert len(result) == 3
        assert result[0]['character'] == 'A'
        assert result[1]['character'] == 'B'
        assert result[2]['character'] == 'C'

    def test_space_handling(self):
        """Test that spaces are handled correctly."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('A B')

        assert len(result) == 3
        assert result[0]['character'] == 'A'
        assert result[1]['character'] == 'space'
        assert result[1]['image'] is None  # Space has no image
        assert result[2]['character'] == 'B'

    def test_unsupported_characters_skipped(self):
        """Test that unsupported characters are skipped."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('A1B')

        # Should only have A and B, 1 is skipped
        assert len(result) == 2
        assert result[0]['character'] == 'A'
        assert result[1]['character'] == 'B'

    def test_special_characters_skipped(self):
        """Test that special characters are skipped."""
        from text_to_sign import text_to_sign_language

        result = text_to_sign_language('A!@#B')

        assert len(result) == 2
        assert result[0]['character'] == 'A'
        assert result[1]['character'] == 'B'

    def test_full_alphabet(self):
        """Test conversion of full alphabet."""
        from text_to_sign import text_to_sign_language

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = text_to_sign_language(alphabet)

        assert len(result) == 26

        for i, char in enumerate(alphabet):
            assert result[i]['character'] == char


class TestValidateImages:
    """Tests for the validate_images function."""

    def test_validate_images_returns_dict(self):
        """Test that validate_images returns a dictionary."""
        from text_to_sign import validate_images

        result = validate_images()

        assert isinstance(result, dict)
        assert len(result) == 27  # 26 letters + space

    def test_space_always_valid(self):
        """Test that space character is always valid."""
        from text_to_sign import validate_images

        result = validate_images()

        assert result[' '] is True


class TestGetImageBase64:
    """Tests for the get_image_base64 function."""

    def test_none_path_returns_none(self):
        """Test that None path returns None."""
        from text_to_sign import get_image_base64

        result = get_image_base64(None)
        assert result is None

    def test_nonexistent_file_returns_none(self):
        """Test that nonexistent file returns None."""
        from text_to_sign import get_image_base64

        result = get_image_base64('/nonexistent/path/image.png')
        assert result is None
