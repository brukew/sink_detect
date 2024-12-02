import PIL
from PIL import Image
import os
import shutil

import random

def manual_split(data, train_ratio=0.7, val_ratio=0.2):
    random.shuffle(data)
    train_size = int(len(data) * train_ratio)
    val_size = int(len(data) * val_ratio)
    train = data[:train_size]
    val = data[train_size:train_size + val_size]
    test = data[train_size + val_size:]
    return train, val, test

# Input and output folder paths
base_dir = "/Users/brukewossenseged/Documents/tinyML/sink_data"  # Replace with your dataset path
output_dir = "/Users/brukewossenseged/Documents/tinyML/split_data"  # Output folder for split data

# Classes and subfolders for rotation
rotate_folders = [
    "dirty_sink_0", "dirty_sink_4",
    "clean_sink_0", "clean_sink_2", "clean_sink_3"
]

# Target size for resizing images
target_size = (1280, 720)  # Set the desired image size

# Ensure output folders exist
splits = ["train", "val", "test"]
classes = ["clean_sink", "dirty_sink"]
for split in splits:
    for cls in classes:
        os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

def is_image_valid(image_path):
    """Check if an image can be opened."""
    try:
        img = Image.open(image_path)
        img.verify()  # Verify the integrity of the image
        return True
    except Exception:
        return False

def process_and_split_images():
    """Process images: rotate, resize, and split them into train/val/test."""
    for cls in classes:
        class_path = os.path.join(base_dir, cls)
        all_images = []

        # Include images directly in the class folder
        main_images = [os.path.join(class_path, f) for f in os.listdir(class_path)
                       if f.endswith((".png", ".jpg"))]
        all_images.extend(main_images)

        # Include images from subfolders
        for subfolder in os.listdir(class_path):
            subfolder_path = os.path.join(class_path, subfolder)
            if os.path.isdir(subfolder_path):
                images = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path)
                          if f.endswith((".png", ".jpg"))]
                all_images.extend(images)

        # Take every fifth image for splitting
        all_images = all_images[::5]

        # Split into train, val, and test
        train_files, val_files, test_files = manual_split(all_images)

        # Process images (rotate, resize) and copy to output
        for split, split_files in zip(splits, [train_files, val_files, test_files]):
            for file in split_files:
                output_folder = os.path.join(output_dir, split, cls)
                process_image(file, output_folder)

def process_image(image_path, output_folder):
    """Rotate, resize, and save an image to the output folder."""
    try:
        img = Image.open(image_path)
        if any(folder in image_path for folder in rotate_folders):
            img = img.rotate(90, PIL.Image.NEAREST, expand = 1)
        # Resize the image
        img = img.resize(target_size)

        # Save to output folder
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        img.save(output_path)
        print(f"Processed and saved: {output_path}")
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")

# Run the script
process_and_split_images()