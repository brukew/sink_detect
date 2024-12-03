import tkinter as tk
import serial
import math
import random
import time
import os
from PIL import Image, ImageTk
from os.path import isfile, join

WINDOW = tk.Tk()
DELAY_1 = tk.Entry(WINDOW)
DELAY_2 = tk.Entry(WINDOW)
IMAGE_DIR = "."
SERIAL_PORT = '/dev/tty.usbmodem1103'  # Replace with your specific port
BAUD_RATE = 115200
SER = None
IMAGE_LIST = []
UART_COMMAND_LIST = []
INDEX = 0
CURRENT_IMAGE = None

def serial_init():
    # UART setup
    global SER
    try:
        SER = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
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
        print(f"Sent: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

def load_dir(path, list):
    """Load images in path including nested directories"""

    for f in os.listdir(f"{IMAGE_DIR}/{path}"):
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
    print(f"{len(clean_sink_list)} clean sink images, {len(dirty_sink_list)} dirty sink images")
    IMAGE_LIST.extend(clean_sink_list + dirty_sink_list)
    random.shuffle(IMAGE_LIST)
    for img in IMAGE_LIST:
        if img in clean_sink_list:
            UART_COMMAND_LIST.append("1")
        else:
            UART_COMMAND_LIST.append("2")


def send_uart():
    """Sends UART command associated with current image"""
    global INDEX
    # send_command(UART_COMMAND_LIST[INDEX])
    if (INDEX == len(IMAGE_LIST)):
        print("Trainig Complete")
        exit()
    print(f"Sent UART {UART_COMMAND_LIST[INDEX]} associated with {IMAGE_LIST[INDEX]}")
    INDEX += 1
    WINDOW.after(int(float(D2)*1000), upload_image)

def upload_image(resize=True):
    """Uploads image to trainer, increments index"""
    global CURRENT_IMAGE
    canvas = tk.Canvas(WINDOW, width=WINDOW.winfo_width(), height=WINDOW.winfo_height())
    temp = Image.open(IMAGE_LIST[INDEX])
    if resize:
        temp = temp.resize((WINDOW.winfo_width(), WINDOW.winfo_height()), Image.LANCZOS)
    img = ImageTk.PhotoImage(temp)
    CURRENT_IMAGE = img
    bg_image = tk.Label(WINDOW, image=img)
    bg_image.place(x=0, y=0, relwidth=1, relheight=1)
    print(f"Uploaded {IMAGE_LIST[INDEX]}")
    canvas.pack()
    WINDOW.after(int(float(D1)*1000), send_uart)


def cycle_images():
    """Add periodic event for upload_image func"""
    global D1, D2
    D1 = DELAY_1.get()
    D2 = DELAY_2.get()
    clear_all_inside_frame()
    upload_image()

def tkinter_init():
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

if __name__ == "__main__":
    #serial_init()
    # send_command("3")  # Enter training mode
    load_images()
    tkinter_init()