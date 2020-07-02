import ctypes
import time
from PIL import Image, ImageEnhance
import os
from multiprocessing import Pool
import atexit


class ImageTransition:

    def __init__(self, input_image, output_image, temporary_dir, debug=True, quality=40, num_of_images=15, direct_wp=False):
        self.image1 = input_image
        self.image2 = output_image
        self.temp_dir = temporary_dir
        self.debug = debug
        self.quality = quality
        self.num_of_images = num_of_images
        self.direct_wp = direct_wp

        self.__check_image_loadable()

        self.clean_dir()
        self.printDebug(f"Temporary Directory: {temporary_dir}")
        self.gen_temporary_imgs()

        atexit.register(self.clean_dir)

    def __check_image_loadable(self):
        try:
            Image.open(self.image1)
            Image.open(self.image2)
        except:
            raise IOError("Error loading file")

    def setwp(self, img):#works only for windows
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img, 0)

    #changes brightness for a PIL Image
    def change_brightness(self, img:Image, value):
        enhancer = ImageEnhance.Brightness(img)
        enhanced_im = enhancer.enhance(value)
        return enhanced_im

    def clean_dir(self):
        self.printDebug("> Deleting temp files...")
        for filename in os.listdir(self.temp_dir):
            if filename.split(".")[1] in ["png","jpg"]:
                try:
                    os.remove(os.path.join(self.temp_dir, filename))
                except:
                    time.sleep(2)
                    os.remove(os.path.join(self.temp_dir, filename))

    def transition_brightness(self, fps=25):
        print("> Transition")
        for filename in sorted(os.listdir(self.temp_dir), key=lambda x: int(os.path.splitext(x)[0])):
            file_type = filename[-3:]
            if file_type in ["png", "jpg"]:
                #print(filename)
                time.sleep(1 / fps)
                if self.direct_wp:
                    self.setwp(os.path.join(self.temp_dir, filename))
                else:
                    yield os.path.join(self.temp_dir, filename)

        if self.direct_wp:
            self.setwp(self.image2)
        else:
            yield self.image2

        time.sleep(5)
        self.clean_dir()

    def printDebug(self, msg):
        if self.debug:
            print(msg)

    def worker(self, work_data):

        counter = abs(work_data[1])

        if work_data[1] <= 0:
            value = round(0 - (work_data[1] * (1 / self.num_of_images)), 2)
            counter += (self.num_of_images)
        else:
            value = round(1 - (work_data[1] * (1 / self.num_of_images)), 2)

        temp_img = Image.open(work_data[0])
        # temp_img.thumbnail([1280, 720], Image.ANTIALIAS)  # resize for better performace
        temp_img.thumbnail([1920, 1080], Image.ANTIALIAS)

        temp_img = self.change_brightness(temp_img, value=value)

        #error without this
        if temp_img.mode in ("RGBA", "P"):
            temp_img = temp_img.convert("RGB")

        temp_img.save(self.temp_dir+"/{:02d}.jpg".format(counter), optimize=True, quality=self.quality)

    def load(self):
        values = []

        for i in range(1, self.num_of_images + 1):
            values.append((self.image1, i))

        for i in range(1, self.num_of_images + 1):
            values.append((self.image2, -i))

        return values

    def gen_temporary_imgs(self):
        p = Pool(processes=2)
        p.map(self.worker, self.load())
        self.printDebug("> Generated temporary images")


