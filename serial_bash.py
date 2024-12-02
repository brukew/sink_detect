import serial
import time
import os
from PIL import Image

# UART configuration
SERIAL_PORT = '/dev/tty.usbmodem1103'  # Replace with your specific port
BAUD_RATE = 115200

# Dataset path
train_dir = "/Users/brukewossenseged/Documents/tinyML/split_data/train"

# UART setup
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"Error connecting to serial port: {e}")
    exit()

def send_command(command):
    """Send a single command to the MCU."""
    try:
        ser.write(command.encode())
        print(f"Sent: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

def display_image(image_path):
    """Display the image using Pillow."""
    img = Image.open(image_path)
    # img.resize((5120, 2880))
    img.show()  # This opens the default image viewer on your system

def process_images():
    """Process images and sync with UART commands."""
    send_command("3")  # Enter training mode

    import random

    # Collect all images across categories
    images_list = []

    for category in os.listdir(train_dir):
        category_path = os.path.join(train_dir, category)
        if not os.path.isdir(category_path):
            continue
        category_images = []
        for image_name in os.listdir(category_path):
            image_path = os.path.join(category_path, image_name)
            if image_name.endswith((".png", ".jpg")):
                # Store image path along with its category
                category_images.append((image_path, category))
        images_list.append(category_images)
    
    most_images = max(images_list, key=lambda l: len(l))

    images_list[0] *= int(len(most_images)/len(images_list[0]))
    images_list[1] *= int(len(most_images)/len(images_list[1]))

    print(f"Number {images_list[0][0][1]}: {len(images_list[0])}")
    print(f"Number {images_list[1][0][1]}: {len(images_list[1])}")

    time.sleep(2)

    # Shuffle the collected images
    all_images = []
    for lst in images_list:
        all_images.extend(lst)

    random.shuffle(all_images)

    # Process the images in random order
    for image_path, category in all_images:
        print(f"Processing image: {image_path} from category: {category}")

        # Display the image
        try:
            display_image(image_path)

            time.sleep(0.5)

            # Send UART command based on category
            if "clean_sink" in category.lower():
                send_command("1")  # Set ground truth to "class 1"
            elif "dirty_sink" in category.lower():
                send_command("2")  # Set ground truth to "class 0")

            # Delay to sync with the camera's frame rate
            time.sleep(0.5)
        except Exception as e:
            print(f"Something failed: {e}")

def main():
    try:
        process_images()
    finally:
        # Close UART connection
        ser.close()
        print("Serial connection closed.")

main()
