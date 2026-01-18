"""
Text to Sign Module

This module converts text input into sign language image representations.
It maps each letter to its corresponding ASL fingerspelling image.
"""

import os
import base64
import logging
from io import BytesIO
from typing import Optional
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

# Get base directory for image paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTER_IMAGES_DIR = os.path.join(BASE_DIR, '..', 'datasets', 'letter_images')

# Mapping of characters to their sign language image paths
SIGN_LANGUAGE_IMAGES: dict[str, Optional[str]] = {
    'A': os.path.join(LETTER_IMAGES_DIR, 'A.png'),
    'B': os.path.join(LETTER_IMAGES_DIR, 'B.png'),
    'C': os.path.join(LETTER_IMAGES_DIR, 'C.png'),
    'D': os.path.join(LETTER_IMAGES_DIR, 'D.png'),
    'E': os.path.join(LETTER_IMAGES_DIR, 'E.png'),
    'F': os.path.join(LETTER_IMAGES_DIR, 'F.png'),
    'G': os.path.join(LETTER_IMAGES_DIR, 'G.png'),
    'H': os.path.join(LETTER_IMAGES_DIR, 'H.png'),
    'I': os.path.join(LETTER_IMAGES_DIR, 'I.png'),
    'J': os.path.join(LETTER_IMAGES_DIR, 'J.png'),
    'K': os.path.join(LETTER_IMAGES_DIR, 'K.png'),
    'L': os.path.join(LETTER_IMAGES_DIR, 'L.png'),
    'M': os.path.join(LETTER_IMAGES_DIR, 'M.png'),
    'N': os.path.join(LETTER_IMAGES_DIR, 'N.png'),
    'O': os.path.join(LETTER_IMAGES_DIR, 'O.png'),
    'P': os.path.join(LETTER_IMAGES_DIR, 'P.png'),
    'Q': os.path.join(LETTER_IMAGES_DIR, 'Q.png'),
    'R': os.path.join(LETTER_IMAGES_DIR, 'R.png'),
    'S': os.path.join(LETTER_IMAGES_DIR, 'S.png'),
    'T': os.path.join(LETTER_IMAGES_DIR, 'T.png'),
    'U': os.path.join(LETTER_IMAGES_DIR, 'U.png'),
    'V': os.path.join(LETTER_IMAGES_DIR, 'V.png'),
    'W': os.path.join(LETTER_IMAGES_DIR, 'W.png'),
    'X': os.path.join(LETTER_IMAGES_DIR, 'X.png'),
    'Y': os.path.join(LETTER_IMAGES_DIR, 'Y.png'),
    'Z': os.path.join(LETTER_IMAGES_DIR, 'Z.png'),
    ' ': None  # Space has no image
}


def get_image_base64(image_path: str) -> Optional[str]:
    """Convert an image file to base64 encoded string.

    Args:
        image_path: Path to the image file.

    Returns:
        Base64 encoded string of the image, or None if file not found.
    """
    if not image_path:
        return None

    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {e}")
        return None


def text_to_sign_language(text: str) -> list[dict[str, Optional[str]]]:
    """Convert text to a list of sign language image representations.

    Args:
        text: The text to convert (will be converted to uppercase).

    Returns:
        List of dictionaries containing character and base64 encoded image.
        Each dictionary has 'character' and 'image' keys.
    """
    if not text:
        logger.warning("Empty text provided to text_to_sign_language")
        return []

    text = text.upper()
    images_data: list[dict[str, Optional[str]]] = []

    logger.info(f"Converting text to sign language: {text[:50]}...")

    for char in text:
        if char in SIGN_LANGUAGE_IMAGES:
            img_path = SIGN_LANGUAGE_IMAGES[char]
            if img_path:
                img_base64 = get_image_base64(img_path)
                images_data.append({
                    'character': char,
                    'image': img_base64
                })
            else:
                # Space character
                images_data.append({
                    'character': 'space',
                    'image': None
                })
        else:
            logger.warning(f"Character '{char}' not found in sign language dictionary")

    logger.info(f"Generated {len(images_data)} sign images")
    return images_data


def validate_images() -> dict[str, bool]:
    """Validate that all sign language images exist.

    Returns:
        Dictionary mapping characters to boolean indicating if image exists.
    """
    results = {}
    for char, path in SIGN_LANGUAGE_IMAGES.items():
        if path is None:
            results[char] = True  # Space doesn't need an image
        else:
            results[char] = os.path.exists(path)
            if not results[char]:
                logger.warning(f"Missing image for character '{char}': {path}")
    return results


# Example usage and validation
if __name__ == "__main__":
    print("Validating sign language images...")
    validation = validate_images()

    missing = [char for char, exists in validation.items() if not exists]
    if missing:
        print(f"Missing images for characters: {missing}")
    else:
        print("All images found!")

    # Test conversion
    test_text = "HELLO"
    result = text_to_sign_language(test_text)
    print(f"\nTest conversion of '{test_text}':")
    for item in result:
        status = "OK" if item['image'] else "NO IMAGE"
        print(f"  {item['character']}: {status}")
