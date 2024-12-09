import tkinter as tk
import serial
import math
import random
import time
import os
from PIL import Image, ImageTk
from os.path import isfile
import tqdm
import csv

WINDOW = tk.Tk()
DELAY_1 = tk.Entry(WINDOW)
DELAY_2 = tk.Entry(WINDOW)
IMAGE_DIR = "./sink_data"
SERIAL_PORT = '/dev/tty.usbmodem1103'  # Replace with your specific port
BAUD_RATE = 115200
SER = None
IMAGE_LIST = []
UART_COMMAND_LIST = []
INDEX = 0
CURRENT_IMAGE = None
PBAR = None
DEBUG = False
TRAIN_CSV_FILE = 'train_data.csv'
VAL_CSV_FILE = 'val_data.csv'
TRAIN = True

def csv_init():
    with open(TRAIN_CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['img_file', 'cls', 'correct'])
    with open(VAL_CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['img_file', 'cls', 'correct'])

def serial_init():
    # UART setup
    global SER
    try:
        SER = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        if DEBUG:
            print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Error connecting to serial port: {e}")
        exit()

def clear_all_inside_frame():
    # Iterate through every widget inside the frame
    for widget in WINDOW.winfo_children():
        widget.destroy()  # deleting widget

def send_command(command):
    """Send a single command to the MCU."""
    global SER
    try:
        SER.write(command.encode())
        if DEBUG:
            print(f"Sent: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

def read_answer():
    global SER
    try:
        answer = SER.read(1)
        if DEBUG:
            print(f"Recieved: {answer[-1]}")
        return answer
    except Exception as e:
        print(f"Error reading answer: {e}")

def load_dir(path, list):
    """Load images in path including nested directories"""

    for f in os.listdir(f"{IMAGE_DIR}/{path}"):
        if f.startswith('.'):
            continue

        if isfile(f"{IMAGE_DIR}/{path}/{f}"):
            list.append(f"{IMAGE_DIR}/{path}/{f}")
        else:
            load_dir(f"{path}/{f}", list)

def load_images(balance=True):
    """Load images and shuffle"""
    global IMAGE_LIST, UART_COMMAND_LIST

    clean_sink_list = []
    dirty_sink_list = []
    load_dir("clean_sink", clean_sink_list)
    load_dir("dirty_sink", dirty_sink_list)
    if (balance):
        if len(clean_sink_list) > len(dirty_sink_list):
            dirty_sink_list *= math.ceil(len(clean_sink_list)/len(dirty_sink_list))
            dirty_sink_list = dirty_sink_list[:len(clean_sink_list)]
        else:
            clean_sink_list *= math.ceil(len(dirty_sink_list)/len(clean_sink_list))
            clean_sink_list = clean_sink_list[:len(dirty_sink_list)]
    if DEBUG:
        print(f"{len(clean_sink_list)} clean sink images, {len(dirty_sink_list)} dirty sink images")
    if (balance):
        # shuffle both
        random.shuffle(clean_sink_list)
        random.shuffle(dirty_sink_list)

        # force alternation
        counter1 = 0
        counter2 = 0
        for i in range(len(clean_sink_list)):
            if not i % 3:
                IMAGE_LIST.append(clean_sink_list[counter1])
                counter1 = (counter1 + 1) % len(clean_sink_list)
            else:
                IMAGE_LIST.append(dirty_sink_list[counter2])
                counter2 = (counter2 + 1) % len(dirty_sink_list)
    else:
        # simple shuffle
        IMAGE_LIST.extend(clean_sink_list + dirty_sink_list)
        random.shuffle(IMAGE_LIST)
    for img in IMAGE_LIST:
        if img in clean_sink_list:
            UART_COMMAND_LIST.append("1")
        else:
            UART_COMMAND_LIST.append("2")


def train_uart():
    """Sends UART command associated with current image"""
    global INDEX
    send_command(UART_COMMAND_LIST[INDEX])
    if DEBUG:
        print(f"Sent UART {UART_COMMAND_LIST[INDEX]} associated with {IMAGE_LIST[INDEX]}")
    answer = int(read_answer()[-1])
    with open(TRAIN_CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([IMAGE_LIST[INDEX], UART_COMMAND_LIST[INDEX], answer==1])
    if DEBUG:
        print(f"Predicted {'correct' if answer==1 else 'incorrect'}, ")
    INDEX += 1
    PBAR.update(1)
    PBAR.refresh()
    WINDOW.after(int(float(D2)*1000), upload_image)

def val_uart():
    """Sends UART command associated with current image"""
    global INDEX
    send_command('2')
    answer = int(read_answer()[-1])
    with open(VAL_CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([IMAGE_LIST[INDEX], UART_COMMAND_LIST[INDEX], answer])
    if DEBUG:
        print(f"Predicted {'correct' if answer==1 else 'incorrect'}, ")
    INDEX += 1
    PBAR.update(1)
    PBAR.refresh()
    WINDOW.after(int(float(D2)*1000), upload_image)

def upload_image(resize=True, scaleFactor=2):
    """Uploads image to trainer, increments index"""
    global INDEX, IMAGE_LIST, UART_COMMAND_LIST, TRAIN, CURRENT_IMAGE

    if (INDEX == len(IMAGE_LIST)):
        if TRAIN:
            print("Training Complete")
            TRAIN = False
            INDEX = 0
            IMAGE_LIST = VAL_IMAGE_LIST
            UART_COMMAND_LIST = VAL_UART_COMMAND_LIST
            send_command("4")  # Switch device to inference mode
            time.sleep(0.2)
            send_command("1")  # Switch device to validation mode
        else:
            print("Validation Complete")
            WINDOW.quit()

    canvas = tk.Canvas(WINDOW, width=WINDOW.winfo_width(), height=WINDOW.winfo_height())
    temp = Image.open(IMAGE_LIST[INDEX])
    if resize:
        temp = temp.resize((int(WINDOW.winfo_width()/scaleFactor), int(WINDOW.winfo_height()/scaleFactor)), Image.LANCZOS)
    img = ImageTk.PhotoImage(temp)
    CURRENT_IMAGE = img
    bg_image = tk.Label(WINDOW, image=img)
    bg_image.place(x=0, y=0, relwidth=1, relheight=1)
    bg_image.configure(background="white")
    if DEBUG:
        print(f"Uploaded {IMAGE_LIST[INDEX]}")
    canvas.pack()
    WINDOW.after(int(float(D1)*1000), train_uart if TRAIN else val_uart)


def cycle_images():
    """Add periodic event for upload_image func"""
    global D1, D2
    D1 = DELAY_1.get()
    D2 = DELAY_2.get()
    clear_all_inside_frame()
    upload_image()

def tkinter_init():
    """Set up tkinter window and progress bar"""
    global PBAR

    PBAR = tqdm.tqdm(range(len(IMAGE_LIST)))
    WINDOW.title("Trainer")
    WINDOW.attributes("-fullscreen", True)
    tk.Label(WINDOW, text="Pre UART Command Delay (s)").grid(row=0)
    tk.Label(WINDOW, text="Post UART Command Delay (s)").grid(row=1)
    DELAY_1.grid(row=0, column=1)
    DELAY_2.grid(row=1, column=1)
    DELAY_1.insert(0, "1")
    DELAY_2.insert(0, "1")
    tk.Button(WINDOW, text="Start", command=cycle_images).grid(row=2)
    WINDOW.mainloop()

import random

SEED = 42  # Specific random seed for reproducibility
TRAIN_SPLIT = 0.8  # 80% training, 20% validation
TRAIN_IMAGE_LIST = []
VAL_IMAGE_LIST = []
TRAIN_UART_COMMAND_LIST = []
VAL_UART_COMMAND_LIST = []

def split_dataset():
    """Split the dataset into training and validation sets."""
    global IMAGE_LIST, UART_COMMAND_LIST
    global TRAIN_IMAGE_LIST, VAL_IMAGE_LIST
    global TRAIN_UART_COMMAND_LIST, VAL_UART_COMMAND_LIST

    clean_sink_list = []
    dirty_sink_list = []
    load_dir("clean_sink", clean_sink_list)
    load_dir("dirty_sink", dirty_sink_list)

    # Balance datasets
    if len(clean_sink_list) > len(dirty_sink_list):
        dirty_sink_list *= math.ceil(len(clean_sink_list) / len(dirty_sink_list))
        dirty_sink_list = dirty_sink_list[:len(clean_sink_list)]
    else:
        clean_sink_list *= math.ceil(len(dirty_sink_list) / len(clean_sink_list))
        clean_sink_list = clean_sink_list[:len(dirty_sink_list)]

    # Shuffle with seed
    random.seed(SEED)
    random.shuffle(clean_sink_list)
    random.shuffle(dirty_sink_list)

    # Split datasets into training and validation sets
    clean_train_count = int(TRAIN_SPLIT * len(clean_sink_list))
    dirty_train_count = int(TRAIN_SPLIT * len(dirty_sink_list))

    clean_train = clean_sink_list[:clean_train_count]
    clean_val = clean_sink_list[clean_train_count:]
    dirty_train = dirty_sink_list[:dirty_train_count]
    dirty_val = dirty_sink_list[dirty_train_count:]

    # Combine datasets while maintaining the pattern
    def combine_with_pattern(clean, dirty):
        combined_list = []
        commands = []
        counter1, counter2 = 0, 0
        for i in range(len(clean)):
            if not i % 3:
                combined_list.append(clean[counter1])
                commands.append("1")  # Command for clean sink
                counter1 += 1
            else:
                combined_list.append(dirty[counter2])
                commands.append("2")  # Command for dirty sink
                counter2 += 1
        return combined_list, commands

    # Training and validation sets
    TRAIN_IMAGE_LIST, TRAIN_UART_COMMAND_LIST = combine_with_pattern(clean_train, dirty_train)
    VAL_IMAGE_LIST, VAL_UART_COMMAND_LIST = combine_with_pattern(clean_val, dirty_val)

# Update main block to include split and validation
if __name__ == "__main__":
    csv_init()
    serial_init()
    send_command("3")  # Enter training mode
    split_dataset()  # Split dataset into training and validation
    IMAGE_LIST = TRAIN_IMAGE_LIST  # Use training images for training phase
    UART_COMMAND_LIST = TRAIN_UART_COMMAND_LIST
    tkinter_init()  # Begin training/validation
