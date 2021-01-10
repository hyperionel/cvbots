import cv2 as cv
import numpy as np
import os
import keyboard
import pyautogui
import time
from PIL import Image
from PIL import ImageOps
from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
from edgefilter import EdgeFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# initialize the WindowCapture class
wincap = WindowCapture('Path of Exile')
# initialize the Vision class
vision_map = Vision('poe_waypoint_crop.png')
# initialize the trackbar window
vision_map.init_control_gui()

# map filter
hsv_map_filter = HsvFilter(96, 66, 66, 179, 255, 255, 95, 30, 25, 107)

loop_time = time.time()
while True:

    valid_fog = []
    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # pre-process the image
    processed_image = vision_map.apply_hsv_filter(screenshot, hsv_map_filter)
    
    fog_range_r = range(0, 45)
    fog_range_g = range(65, 90)
    map_range_r = range(50, 80)
    map_range_g = range(55, 64)

    for x in range(0, 720):
        for y in range(0, 1080):
            r = processed_image.item(x, y, 2)
            g = processed_image.item(x, y, 1)
            b = processed_image.item(x, y, 0)
            if r in fog_range_r and g in fog_range_g:
                # processed_image.itemset((x, y), (0, 255, 0))
                # print('Am GREEN')
                # valid_fog.append([x, y])
                processed_image.itemset((x, y, 2), 0)
                processed_image.itemset((x, y, 1), 255)
                processed_image.itemset((x, y, 0), 0)
            if r in map_range_r and g in map_range_g:
                # print('Am RED')
                # processed_image.itemset((x, y), (255, 0, 0))
                processed_image.itemset((x, y, 2), 255)
                processed_image.itemset((x, y, 1), 0)
                processed_image.itemset((x, y, 0), 0)

    # print(valid_fog)
    # do bot actions

    #find most upwards value
    # for n, x in enumerate(valid_fog):
    #     valid_fog[n] = wincap.get_screen_position((valid_fog[n][0], valid_fog[n][1]))
    
    
    cv.imshow('Processed', processed_image)

    # debug the loop rate
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')