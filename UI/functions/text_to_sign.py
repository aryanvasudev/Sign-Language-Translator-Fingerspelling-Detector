import os
from PIL import Image
import base64
from io import BytesIO

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

def get_image_base64(image_path):
    if image_path:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
    return None

def text_to_sign_language(text):
    text = text.upper()
    images_data = []
    
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
                images_data.append({
                    'character': 'space',
                    'image': None
                })
        else:
            print(f"Character '{char}' not found in dictionary.")
            
    return images_data
