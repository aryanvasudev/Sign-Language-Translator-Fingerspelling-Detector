import os
import time
from PIL import Image

# Dictionary mapping letters to image file paths
SIGN_LANGUAGE_IMAGES = {
    'A': 'path_to_images/A.png',
    'B': 'path_to_images/B.png',
    # Add paths for all letters
    'Z': 'path_to_images/Z.png',
    ' ': None  # Space is represented by a blank screen
}

def display_image(image_path):
    """Displays the image using PIL."""
    if image_path:
        img = Image.open(image_path)
        img.show()
        time.sleep(1)  # Display each letter for 1 second
        img.close()  # Close the image after displaying
    else:
        # Blank screen for space
        print("Blank screen (space)")
        time.sleep(1)  # Display blank for 1 second

def text_to_sign_language(text):
    """Converts text to sign language images."""
    text = text.upper()  # Convert text to uppercase for consistency
    for char in text:
        if char in SIGN_LANGUAGE_IMAGES:
            display_image(SIGN_LANGUAGE_IMAGES[char])
        else:
            print(f"Character '{char}' not found in dictionary.")

# Example usage
input_text = "HELLO WORLD"
text_to_sign_language(input_text)

