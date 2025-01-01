import os
import shutil
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import ImageDataGenerator # If vs code shows line under this import, then run this command in terminal: pip install tensorflow and if the line still not erase leave it as it is.
from tqdm import tqdm

def augment_images(folder_path, save_to_dir=None, augmentations=None):
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    if augmentations is None:
        augmentations = {
            "rotation_range": 30,
            "width_shift_range": 0.2,
            "height_shift_range": 0.2,
            "shear_range": 0.2,
            "zoom_range": 0.2,
            "horizontal_flip": True,
            "fill_mode": 'nearest'
        }

    datagen = ImageDataGenerator(**augmentations)

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

    if save_to_dir and not os.path.exists(save_to_dir):
        os.makedirs(save_to_dir)

    if save_to_dir:
        print("\nCopying original images to the save directory...")
        for filename in tqdm(image_files, desc="Copying original images"):
            source_path = os.path.join(folder_path, filename)
            dest_path = os.path.join(save_to_dir, filename)
            try:
                shutil.copy(source_path, dest_path)
            except Exception as e:
                print(f"Error copying {filename}: {e}")

    print("\nStarting image augmentations...")
    for filename in tqdm(image_files, desc="Augmenting images"):
        file_path = os.path.join(folder_path, filename)

        try:
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = np.expand_dims(img, axis=0)
            i = 0
            for batch in datagen.flow(img, batch_size=1, save_to_dir=save_to_dir or folder_path, 
                                       save_prefix=os.path.splitext(filename)[0], save_format='jpeg'):
                i += 1
                if i >= 5: 
                    break

        except Exception as e:
            print(f"Error processing {filename}: {e}")

def increment_path(path):
    base, last_part = os.path.split(path.rstrip(os.sep))
    if last_part.isdigit():
        incremented_part = str(int(last_part) + 1)
        return os.path.join(base, incremented_part)
    else:
        return os.path.join(path + "_1")

def confirm_paths(folder_path, save_to_dir):
    print(f"\nImage folder path: {folder_path}")
    print(f"Save-to folder path: {save_to_dir}")
    confirm = input("Do you want to proceed with these paths? (y/n): ").strip().lower()
    return confirm == 'y'

if __name__ == "__main__":
    print("\nWelcome to the image augmentation program!")
    folder_path = None
    save_to_dir = None

    while True:
        if folder_path is None and save_to_dir is None:
            folder_path = input("Enter the path to the folder containing images: ")
            save_to_dir = input("Enter the path to save augmented images (or leave blank to save in the same folder): ")
            save_to_dir = save_to_dir.strip() or None
        else:
            try:
                folder_path = increment_path(folder_path)
                if save_to_dir:
                    save_to_dir = increment_path(save_to_dir)
                print("\nIncremented paths:")
                if not confirm_paths(folder_path, save_to_dir):
                    print("Exiting program. Goodbye!")
                    break
            except Exception as e:
                print(f"Error incrementing paths: {e}")
                break
        if not confirm_paths(folder_path, save_to_dir):
            print("Exiting program. Goodbye!")
            break
        augment_images(folder_path, save_to_dir)

        repeat = input("\nDo you want to augment more images? (y/n): ").strip().lower()
        if repeat != 'y':
            print("\nThank you for using the image augmentation program.\n\n Now make the dataset using the create_Dataset.py file.")
            print("\nExiting program. Goodbye!")
            break
