from PIL import Image
import serial
import time
import os

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
    time.sleep(0.5)
    """Send a single command to the MCU."""
    try:
        ser.write(command.encode())
        print(f"Sent: {command}")
        time.sleep(1)  # Short delay for MCU to process the command
    except Exception as e:
        print(f"Error sending command: {e}")

def display_image(image_path):
    """Display the image using Pillow."""
    img = Image.open(image_path)
    img.show()  # This opens the default image viewer on your system
    time.sleep()  # Wait for ~300ms to simulate the camera frame rate
    # try:
    #     img = Image.open(image_path)
    #     img.show()  # This opens the default image viewer on your system
    #     time.sleep()  # Wait for ~300ms to simulate the camera frame rate
    # except Exception as e:
    #     print(f"Error displaying image: {e}")

def process_images():
    """Process images and sync with UART commands."""
    send_command("3")  # Enter training mode

    import random

    # Collect all images across categories
    all_images = []

    for category in os.listdir(train_dir):
        category_path = os.path.join(train_dir, category)
        if not os.path.isdir(category_path):
            continue

        for image_name in os.listdir(category_path):
            image_path = os.path.join(category_path, image_name)
            if image_name.endswith((".png", ".jpg")):
                # Store image path along with its category
                all_images.append((image_path, category))

    # Shuffle the collected images
    random.shuffle(all_images)

    # Process the images in random order
    for image_path, category in all_images:
        print(f"Processing image: {image_path} from category: {category}")

        # Display the image
        try:
            display_image(image_path)

            # Send UART command based on category
            if "clean_sink" in category.lower():
                send_command("1")  # Set ground truth to "class 1"
            elif "dirty_sink" in category.lower():
                send_command("2")  # Set ground truth to "class 0")

            # Delay to sync with the camera's frame rate
            time.sleep(1)
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
