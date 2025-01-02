import os
import time
from PIL import Image

# Dictionary mapping letters to image file paths
SIGN_LANGUAGE_IMAGES = {
    'A': 'datasets/letter_images/A.png',
    'B': 'datasets/letter_images/B.png',
    'C': 'datasets/letter_images/C.png',
    'D': 'datasets/letter_images/D.png',
    'E': 'datasets/letter_images/E.png',
    'F': 'datasets/letter_images/F.png',
    'G': 'datasets/letter_images/G.png',
    'H': 'datasets/letter_images/H.png',
    'I': 'datasets/letter_images/I.png',
    'J': 'datasets/letter_images/J.png',
    'K': 'datasets/letter_images/K.png',
    'L': 'datasets/letter_images/L.png',
    'M': 'datasets/letter_images/M.png',
    'N': 'datasets/letter_images/N.png',
    'O': 'datasets/letter_images/O.png',
    'P': 'datasets/letter_images/P.png',
    'Q': 'datasets/letter_images/Q.png',
    'R': 'datasets/letter_images/R.png',
    'S': 'datasets/letter_images/S.png',
    'T': 'datasets/letter_images/T.png',
    'U': 'datasets/letter_images/U.png',
    'V': 'datasets/letter_images/V.png',
    'W': 'datasets/letter_images/W.png',
    'X': 'datasets/letter_images/X.png',
    'Y': 'datasets/letter_images/Y.png',
    'Z': 'datasets/letter_images/Z.png',
    ' ': None 
}

def display_image(image_path):
    if image_path:
        img = Image.open(image_path)
        img.show()
        time.sleep(1)
        img.close()  
    else:
        
        print("Blank screen (space)")
        time.sleep(1)

def text_to_sign_language(text):
    
    text = text.upper()
    for char in text:
        if char in SIGN_LANGUAGE_IMAGES:
            display_image(SIGN_LANGUAGE_IMAGES[char])
        else:
            print(f"Character '{char}' not found in dictionary.")

# Example usage
input_text = "HELLO WORLD"
text_to_sign_language(input_text)

