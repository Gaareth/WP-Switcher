# WP-Switcher
Crossplattform Wallpaper Switcher

## Installation

* Python3 needs to be installed
* Install the dependencies: `pip install -r requirements.txt`

## Usage

### Basic Usage
`python wallpaper-switcher.py -f {your wallpaper directory}`
### Arguments
Argument | Description
------------ | -------------
-f WP_FOLDER | path to wallpaper folder
-d DELAY | Delay in **seconds** until wallpaper switch
-nsfw NSFW | Includes Not Safe For Work (NSFW) images (**NSFW Images need to be in sub folder called 'NSFW'** and -recursive needs to activated)
-r RECURSIVE| Recursively choosing images (from all sub folders)
-t TRANSITION | Activates a transition between the wallpaper change (**Does not work for KDE.** KDE has an own image transition animation)
--fps FPS | Frames Per Second for the transition
-q QUALITY| Quality of the transition images in percent.
--len_transition LEN_TRANSITION| Number of images used for the transition



## Copyright
Copied most of the crossplatform code for changing the wallpaper from Stackoverflow: https://stackoverflow.com/a/21213504
As far as I know it works for Windows10 and KDE.
