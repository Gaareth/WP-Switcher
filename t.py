import ctypes
import time
from PIL import Image, ImageEnhance
from PIL import Image
import os
import numpy as np
import cv2
from multiprocessing import Pool


image1 = r"C:\Users\Kirstein\Pictures\Hintergrundbilder\background-beautiful-blossom-268533.jpg"
image2 = r"C:\Users\Kirstein\Pictures\Hintergrundbilder\67572-blaue-schoene-hintergrundbilder-1920x1080-fuer-hd.jpg"

def setwp(img):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, img, 0)

def change_brightness(img, value):
    img = Image.open(img)
    enhancer = ImageEnhance.Brightness(img)
    enhanced_im = enhancer.enhance(value)
    return enhanced_im

time.sleep(2)

def clean_dir(dir):
    dir = r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher"
    for filename in os.listdir(dir):
        if filename.split(".")[1] == "png":
            try:
                os.remove(os.path.join(dir, filename))
            except:
                time.sleep(2)
                os.remove(os.path.join(dir, filename))



def prepare_transition(img, direction=+1):
    for i in range(1, 21):
        if direction == 1:
            id = 0
            value = 0 + (i * 0.05)
        else:
            id = 1
            value = 1 - (i * 0.05)

        value = round(value,2)
        print(value)

        temp_img = change_brightness(img, value=value)
        temp_img.save(r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher\temp{},{}.png".format(id,i))


def transition_brightness():
    dir = r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher\img"
    for filename in sorted(os.listdir(dir)):
        type = filename[-3:]

        if type in ["png","jpg"]:
            print(filename)
            time.sleep(1/25)
            setwp(os.path.join(dir, filename))


def worker(work_data):
    counter = abs(work_data[1])

    value = 1 - (work_data[1] * (1 / 15))
    value = round(value, 2)

    if work_data[1] <= 0:
        value = 0 - (work_data[1] * (1 / 15))
        value = round(value, 2)
        counter+=30

    print(f"VALUE: {value} IMAGE: {work_data[0]} COUNTER: {counter}")

    temp_img = change_brightness(work_data[0], value=value)


    temp_img.save(
        r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher\img\temp{:02d}.jpg".format(counter), optimize=True, quality=40)

def load(im1, im2):
    values = []
    n = 15
    for i in range(1, n+1):
        #value = 1 - (i * (1/n))
        #value = round(value,2)
        values.append((im1,i))

    for i in range(1, n+1):
        values.append((im2,-i))


    return values

def loop():
    total_frames = len(os.listdir(r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher\img"))
    current_frame = 1
    print(total_frames)
    while True:
        if current_frame != total_frames:
            print(current_frame)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, r"C:\Users\Kirstein\Desktop\Coding\python\Workspace\python2\wallpaper-switcher\img\temp{}.jpg".format(current_frame), 0)
            time.sleep(1 / 30)
            current_frame += 1
        else:
            current_frame = 0

def pool_handler():
    p = Pool(16)
    p.map(worker, load(image1,image2))


if __name__ == "__main__":
    transition_brightness()

    #pool_handler()



#time.sleep(5)
#clean_dir("")
