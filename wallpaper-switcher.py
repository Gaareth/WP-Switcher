import os
import re
import sys
from collections import defaultdict
import random
import time
import subprocess
import ctypes
import importlib
import argparse

img_transition = importlib.import_module("image-transition")


class WallpaperSwitcher():

    recent_wp = defaultdict()
    current_wp = ""

    def __init__(self, wallpaper_folder=r"C:\Users\Kirstein\Pictures\Hintergrundbilder", wait_time=10, transition = True, fps_transition = 20, quality_transition = 100, num_of_images_transition = 20):
        self.WP_FOLDER = wallpaper_folder
        self.wait = wait_time

        self.transition = transition
        self.fps_trans = fps_transition
        self.quality_tran = quality_transition
        self.num_of_images_tran = num_of_images_transition



        print("-------------Settings-------------")
        print("Wallpaper folder:",wallpaper_folder)
        print("Delay:",wait_time)
        print("Transition:",transition)
        print("FPS:",fps_transition)
        print("Quality:",quality_transition)
        print("Transition Length:",num_of_images_transition)
        print("-------------Settings-------------\n")

    def get_desktop_environment(self):
        # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=1139057
        if sys.platform in ["win32", "cygwin"]:
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else:  # Most likely either a POSIX system or something not much common
            desktop_session = os.environ.get("DESKTOP_SESSION")
            if desktop_session is not None:  # easier to match if we doesn't have  to deal with caracter cases
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                       "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde"]:
                    return desktop_session
                ## Special cases ##
                # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
                # There is no guarantee that they will not do the same with the other desktop environments.
                elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                    return "xfce4"
                elif desktop_session.startswith("ubuntu"):
                    return "unity"
                elif desktop_session.startswith("lubuntu"):
                    return "lxde"
                elif desktop_session.startswith("kubuntu"):
                    return "kde"
                elif desktop_session.startswith("razor"):  # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"):  # e.g. wmaker-common
                    return "windowmaker"
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                return "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                    return "gnome2"
            # From http://ubuntuforums.org/showthread.php?t=652320
            elif self.is_running("xfce-mcs-manage"):
                return "xfce4"
            elif self.is_running("ksmserver"):
                return "kde"
        return "unknown"

    def is_running(self, process):
        # From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
        # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
        try:  # Linux/Unix
            s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
        except:  # Windows
            s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False

    def set_wallpaper(self, file_loc, first_run):
        """ Code copied from: https://stackoverflow.com/a/21213504"""

        # Note: There are two common Linux desktop environments where
        # I have not been able to set the desktop background from
        # command line: KDE, Enlightenment
        desktop_env = self.get_desktop_environment()
        file_loc = os.path.normpath(file_loc)

        if first_run:
            print(f"Desktop Environment: {desktop_env}")
            print(f"Wallpaper: {file_loc}")

        try:
            if desktop_env in ["gnome", "unity", "cinnamon"]:
                uri = "'file://%s'" % file_loc
                try:
                    SCHEMA = "org.gnome.desktop.background"
                    KEY = "picture-uri"
                    gsettings = Gio.Settings.new(SCHEMA)
                    gsettings.set_string(KEY, uri)
                except:
                    args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
                    subprocess.Popen(args)
            elif desktop_env == "mate":
                try:  # MATE >= 1.6
                    # info from http://wiki.mate-desktop.org/docs:gsettings
                    args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % file_loc]
                    subprocess.Popen(args)
                except:  # MATE < 1.6
                    # From https://bugs.launchpad.net/variety/+bug/1033918
                    args = ["mateconftool-2", "-t", "string", "--set", "/desktop/mate/background/picture_filename",
                            '"%s"' % file_loc]
                    subprocess.Popen(args)
            elif desktop_env == "gnome2":  # Not tested
                # From https://bugs.launchpad.net/variety/+bug/1033918
                args = ["gconftool-2", "-t", "string", "--set", "/desktop/gnome/background/picture_filename",
                        '"%s"' % file_loc]
                subprocess.Popen(args)
            ## KDE4 is difficult
            ## see http://blog.zx2c4.com/699 for a solution that might work
            elif desktop_env in ["kde3", "trinity"]:
                # From http://ubuntuforums.org/archive/index.php/t-803417.html
                args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_loc
                subprocess.Popen(args, shell=True)
            elif desktop_env == "xfce4":
                # From http://www.commandlinefu.com/commands/view/2055/change-wallpaper-for-xfce4-4.6.0
                if first_run:
                    args0 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s",
                             file_loc]
                    args1 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style",
                             "-s",
                             "3"]
                    args2 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s",
                             "true"]
                    subprocess.Popen(args0)
                    subprocess.Popen(args1)
                    subprocess.Popen(args2)
                args = ["xfdesktop", "--reload"]
                subprocess.Popen(args)

            elif desktop_env in ["fluxbox", "jwm", "openbox", "afterstep"]:
                # http://fluxbox-wiki.org/index.php/Howto_set_the_background
                # used fbsetbg on jwm too since I am too lazy to edit the XML configuration
                # now where fbsetbg does the job excellent anyway.
                # and I have not figured out how else it can be set on Openbox and AfterSTep
                # but fbsetbg works excellent here too.
                try:
                    args = ["fbsetbg", file_loc]
                    subprocess.Popen(args)
                except:
                    sys.stderr.write("ERROR: Failed to set wallpaper with fbsetbg!\n")
                    sys.stderr.write("Please make sre that You have fbsetbg installed.\n")
            elif desktop_env == "icewm":
                # command found at http://urukrama.wordpress.com/2007/12/05/desktop-backgrounds-in-window-managers/
                args = ["icewmbg", file_loc]
                subprocess.Popen(args)
            elif desktop_env == "blackbox":
                # command found at http://blackboxwm.sourceforge.net/BlackboxDocumentation/BlackboxBackground
                args = ["bsetbg", "-full", file_loc]
                subprocess.Popen(args)
            elif desktop_env == "lxde":
                args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_loc
                subprocess.Popen(args, shell=True)
            elif desktop_env == "windowmaker":
                # From http://www.commandlinefu.com/commands/view/3857/set-wallpaper-on-windowmaker-in-one-line
                args = "wmsetbg -s -u %s" % file_loc
                subprocess.Popen(args, shell=True)
            ## NOT TESTED BELOW - don't want to mess things up ##
            # elif desktop_env=="enlightenment": # I have not been able to make it work on e17. On e16 it would have been something in this direction
            #    args = "enlightenment_remote -desktop-bg-add 0 0 0 0 %s" % file_loc
            #    subprocess.Popen(args,shell=True)
            # elif desktop_env=="windows": #Not tested since I do not run this on Windows
            #    #From https://stackoverflow.com/questions/1977694/change-desktop-background
            #    import ctypes
            #    SPI_SETDESKWALLPAPER = 20
            #    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, file_loc , 0)
            # elif desktop_env=="mac": #Not tested since I do not have a mac
            #    #From https://stackoverflow.com/questions/431205/how-can-i-programatically-change-the-background-in-mac-os-x
            #    try:
            #        from appscript import app, mactypes
            #        app('Finder').desktop_picture.set(mactypes.File(file_loc))
            #    except ImportError:
            #        #import subprocess
            #        SCRIPT = """/usr/bin/osascript<<END
            #        tell application "Finder" to
            #        set desktop picture to POSIX file "%s"
            #        end tell
            #        END"""
            #        subprocess.Popen(SCRIPT%file_loc, shell=True)
            elif desktop_env in ["windows"]:
                ctypes.windll.user32.SystemParametersInfoW(20, 0, file_loc, 0)
            else:
                if first_run:  # don't spam the user with the same message over and over again
                    sys.stderr.write("Warning: Failed to set wallpaper. Your desktop environment is not supported.")
                    sys.stderr.write("You can try manually to set Your wallpaper to %s" % file_loc)
                return False
            return True
        except:
            sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
            return False

    def get_home_dir(self):
        if sys.platform == "cygwin":
            home_dir = os.getenv('HOME')
        else:
            home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
        if home_dir is not None:
            return os.path.normpath(home_dir)
        else:
            raise KeyError("Neither USERPROFILE or HOME environment variables set.")

    def init_recent_wps(self):
        self.recent_wp = {os.path.join(self.WP_FOLDER, filename): float("-inf") for filename in os.listdir(self.WP_FOLDER)}

    def load_wallpapers(self):
        wallpapers = {os.path.join(self.WP_FOLDER, filename):self.recent_wp[os.path.join(self.WP_FOLDER, filename)] for filename in os.listdir(self.WP_FOLDER) if filename[-3:] in ["png", "jpg", "jpeg", "bmp"] }
        wallpapers = [x[0] for x in sorted(wallpapers.items(), key=lambda kv: kv[1], reverse=True)]
        return wallpapers

    def choose_wallpaper(self):
        wp = self.load_wallpapers()

        distributed_wps = []
        for w in wp:
            distributed_wps.extend([w]*(wp.index(w)+1))

        random_wp = random.choice(distributed_wps)
        print(f"Random Wallpaper: {random_wp}")

        return random_wp

    def run(self):
        self.init_recent_wps()

        while True:
            old_wallpaper = self.current_wp
            new_wallpaper = self.choose_wallpaper()

            temp_dir = os.path.expanduser("~")+"\\temp_img"
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)

            if old_wallpaper != "" and self.transition:
                try:
                    itrans = img_transition.ImageTransition(input_image=old_wallpaper, output_image=new_wallpaper, temporary_dir=temp_dir, num_of_images=self.num_of_images_tran, quality=self.quality_tran)
                except Exception as e:
                    sys.stderr.write(f"Error loading Image: {new_wallpaper} or {old_wallpaper}")
                    quit()#TODO: maybe some skip, need to make it properly then

                time.sleep(self.wait)

                for image_path in itrans.transition_brightness(fps=self.fps_trans):
                    self.set_wallpaper(image_path,False) #can safely assume set_wp works (i hope)

            else:
                ret = self.set_wallpaper(new_wallpaper, True)

                if not ret:
                    sys.stderr.write("Critical Error: Shutting down")
                    quit()

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

    ap.add_argument("-d", "--delay",
                    help="Delay until switch")

    ap.add_argument("-t","--transition",type=str2bool,
                    help="Activates a transition between the wallpaper change")

    ap.add_argument("--fps",
                    help="Frames Per Second for the transition")

    ap.add_argument("-q", "--quality",
                    help="Quality of the transition images")

    ap.add_argument("--len_transition",
                    help="Number of images used for the transition")

    args = vars(ap.parse_args())

    wps = WallpaperSwitcher(wallpaper_folder=args["wp_folder"], wait_time=args["delay"], transition=args["transition"], fps_transition=args["fps"], quality_transition=args["quality"], num_of_images_transition=args["len_transition"])
    wps.run()