import cv2 as cv
import numpy as np
import os
import keyboard
import pyautogui
import time
from PIL import Image
from PIL import ImageOps
from win32con import BF_DIAGONAL_ENDBOTTOMLEFT
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

# map filter
hsv_map_filter = HsvFilter(96, 66, 66, 179, 255, 255, 95, 30, 25, 107)

loop_time = time.time()
while(keyboard.is_pressed('q') == False):
    valid_positions = []
    closest_pixel = []
    already_visited = []
    time.sleep(2)

    # pre-process the image
    screenshot = wincap.get_screenshot()
    processed_image = vision_map.apply_hsv_filter(screenshot, hsv_map_filter)

    cv.cvtColor(processed_image, cv.COLOR_BGR2HSV)
    lower = np.array([80, 65, 10], dtype= 'uint8')
    upper = np.array([120, 90, 70], dtype='uint8')
    mask = cv.inRange(processed_image, lower, upper)

    blobDetectorParameters = cv.SimpleBlobDetector_Params()
    blobDetectorParameters.filterByArea = True
    blobDetectorParameters.minArea = 5
    blobDetectorParameters.maxArea = 1000
    blobDetectorParameters.minDistBetweenBlobs = 0
    blobDetectorParameters.filterByCircularity = False
    blobDetectorParameters.filterByColor = False
    blobDetectorParameters.filterByConvexity = False
    blobDetectorParameters.filterByInertia = True
    blobDetectorParameters.minInertiaRatio = 0
    blobDetectorParameters.maxInertiaRatio = 0.1

    detector = cv.SimpleBlobDetector_create(blobDetectorParameters)
    keypoints = detector.detect(mask)
    imageWithKeypoints = cv.drawKeypoints(mask, keypoints, np.array([]), (0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    center_x = int(wincap.w / 2)
    center_y = int(wincap.h / 2)
    center = (center_x, center_y)
    screen_center = wincap.get_screen_position((center_x, center_y))

    valid_positions = []
    for x in keypoints:
        valid_positions.append([int(x.pt[0]), int(x.pt[1])])

    distance_average = lambda x, y: (x[0] - y[0])**2 + (x[1] - y[1])**2
    if len(valid_positions) > 0:
        closest_pixel = min(valid_positions, key=lambda co: distance_average(co, center))
        closest_pixel = wincap.get_screen_position((closest_pixel[0], closest_pixel[1])) 
    else:
        closest_pixel = center
    pyautogui.moveTo(x = closest_pixel[0], y = closest_pixel[1])
    pyautogui.mouseDown()
    time.sleep(1.9)
    pyautogui.mouseUp()

    cv.imshow("Keypoints", imageWithKeypoints)
    
    # cv.imshow('Processed', processed_image)
    # cv.imshow('mask', mask)

    # debug the loop rate
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')