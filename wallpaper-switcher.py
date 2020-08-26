import argparse
import importlib
import os
import random
import signal
import sys
import threading
import time
import traceback
from collections import defaultdict

import cv2
import wallpaper_helper

img_transition = importlib.import_module("image-transition")


class WallpaperSwitcher:
    recent_wp = defaultdict()
    current_wp = ""
    should_sleep = True

    def __init__(self, wallpaper_folder=os.path.join(os.path.expanduser("~"), "Pictures"),
                 wait_time=120, transition=True,
                 fps_transition=20, quality_transition=100, num_of_images_transition=20, nsfw=False,
                 recursive=True, supported_images=None):

        if supported_images is None:
            supported_images = [".png", ".jpg", ".jpeg", ".bmp", ".jpg_large", ".webp"]

        self.WP_FOLDER = wallpaper_folder
        self.wait = wait_time

        self.transition = transition
        self.fps_trans = fps_transition
        self.quality_tran = quality_transition
        self.num_of_images_tran = num_of_images_transition
        self.nsfw = nsfw
        self.recursive = recursive
        self.supported_images = supported_images

        print("-------------Settings-------------")
        print("Wallpaper folder:", wallpaper_folder)
        print("Delay:", wait_time)
        print("Recursive:", recursive)
        print("NSFW:", nsfw)
        print("Transition:", transition)
        print("FPS:", fps_transition)
        print("Quality:", quality_transition)
        print("Transition Length:", num_of_images_transition)
        print("Supported Images:", supported_images)
        print("-------------Settings-------------\n")

    def init_recent_wps(self):
        self.recent_wp = {file: float("-inf") for file in self.load_wallpapers()}

    def load_wallpapers(self):
        if self.recursive:
            all_wallpapers = [os.path.join(dp, f) for dp, dn, fn in os.walk(self.WP_FOLDER) for f in fn
                              if (os.path.splitext(f)[1] in self.supported_images or not len(self.supported_images))
                              and not (not self.nsfw and "NSFW" in dp)]
        else:
            all_wallpapers = {os.path.join(self.WP_FOLDER, filename) for filename in os.listdir(self.WP_FOLDER)
                              if (os.path.splitext(filename)[1] in self.supported_images or not len(
                    self.supported_images))}
        return all_wallpapers

    def sort_wallpapers(self):
        try:
            loaded_wallpapers = self.load_wallpapers()
            print(f"\n> Loaded: {len(loaded_wallpapers)} Wallpapers")
            wallpapers = {filepath: self.recent_wp[filepath] for filepath in loaded_wallpapers}
        except KeyError:
            # might produce endless loop
            traceback.print_exc()
            # Occurs when a new image gets added during the execution
            self.init_recent_wps()
            return self.sort_wallpapers()

        # Items with lower values are in the back
        # A lower value means an item which was picked more time ago => Last Item was picked the longste time ago
        wallpapers = [x[0] for x in sorted(wallpapers.items(), key=lambda kv: kv[1], reverse=True)]
        return wallpapers

    def choose_wallpaper(self):
        wp = self.sort_wallpapers()

        distributed_wps = []
        for w in wp:
            distributed_wps.extend(
                [w] * (wp.index(w) + 1))  # Adds item to list depending on its frequency in the wallpapers

        # Due to the sorting lower values are more likely to be picked

        random_wp = random.choice(distributed_wps)
        height, width, _ = cv2.imread(random_wp).shape
        duplicates = sum([1 for item in distributed_wps if random_wp == item])
        chance = (duplicates / len(distributed_wps)) * 100

        print(
            f"Random Wallpaper: {random_wp} [{width}x{height}] Chance: {chance:.2f}% : {duplicates} / {len(distributed_wps)}")

        return random_wp

    def favorite_wallpaper(self):
        pass

    def sleep(self):
        print("> ", end="")  # Fake input sign
        self.should_sleep = True
        f1 = threading.Thread(target=self.non_blocking_input)
        f1.start()

        t1 = time.time()
        while time.time() - t1 <= self.wait and self.should_sleep:
            pass

    def non_blocking_input(self):
        _input = input("").lower()

        if _input in ["", "skip", "next"]:
            print("Skipping Wallpaper!")
            self.should_sleep = False
            sys.exit(1)  # Stop current thread
        elif _input in ["quit", "exit"]:
            print("> Exit")
            os.kill(os.getpid(), signal.SIGKILL)  # Fucking kill it
        else:
            print(f"command not found: {_input}\n")
            print("> ", end="", flush=True)
            self.non_blocking_input()

    def run(self):
        self.init_recent_wps()

        print(f"Desktop Environment: {wallpaper_helper.get_desktop_environment()}")

        while True:
            old_wallpaper = self.current_wp
            new_wallpaper = self.choose_wallpaper()

            temp_dir = os.path.join(os.path.expanduser("~"), "temp_img")
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)

            if old_wallpaper != "" and self.transition:
                try:
                    itrans = img_transition.ImageTransition(input_image=old_wallpaper, output_image=new_wallpaper,
                                                            temporary_dir=temp_dir,
                                                            num_of_images=self.num_of_images_tran,
                                                            quality=self.quality_tran)
                except IOError:
                    sys.stderr.write(f"Error loading Image: {new_wallpaper} or {old_wallpaper}")
                    quit()  # TODO: maybe some skip, need to make it properly then

                time.sleep(self.wait)

                for image_path in itrans.transition_brightness(fps=self.fps_trans):
                    wallpaper_helper.set_wallpaper(image_path, False)  # can safely assume set_wp works (i hope)

            else:
                ret = wallpaper_helper.set_wallpaper(new_wallpaper, True)
                if not ret:
                    sys.stderr.write("Critical Error: Shutting down")
                    quit()

                self.sleep()

            self.recent_wp[new_wallpaper] = time.time()
            self.current_wp = new_wallpaper


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--wp_folder", required=True,
                    help="Folder of the Wallpapers")

    ap.add_argument("-d", "--delay", default=10, type=int,
                    help="Delay in seconds until wallpaper switch")

    ap.add_argument("-t", "--transition", type=str2bool, default=False,
                    help="Activates a transition between the wallpaper change")

    ap.add_argument("--fps", default=20, type=int,
                    help="Frames Per Second for the transition")

    ap.add_argument("-q", "--quality", default=100, type=int,
                    help="Quality of the transition images")

    ap.add_argument("--len_transition", default=20, type=int,
                    help="Number of images used for the transition")

    ap.add_argument("-nsfw", "--NSFW", default=False, type=str2bool,
                    help="Not Safe For Work (NSFW) images")

    ap.add_argument("-r", "--recursive", default=True, type=str2bool,
                    help="Recursively choosing images (from all sub folders)")

    ap.add_argument("-a", "--allowed_ext", default=[".png", ".jpg", ".jpeg", ".bmp", ".jpg_large", ".webp"], nargs="*",
                    help="Allowed Image extensions specified like thia: '.png', '.jpg'.. . No/Empty means all extensions")

    args = vars(ap.parse_args())
    wps = WallpaperSwitcher(wallpaper_folder=args["wp_folder"], wait_time=args["delay"], transition=args["transition"],
                            fps_transition=args["fps"],
                            quality_transition=args["quality"], num_of_images_transition=args["len_transition"],
                            nsfw=args["NSFW"], recursive=args["recursive"], supported_images=args["allowed_ext"])
    try:
        wps.run()
    except KeyboardInterrupt:
        sys.exit()
