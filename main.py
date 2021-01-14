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
from utils import Utils

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# initialize the WindowCapture class
wincap = WindowCapture('Path of Exile')
# initialize the Vision class
vision_map = Vision()
vision_map_portal = Vision('poe_map_waypoint.png')
# map filter
hsv_map_filter = HsvFilter(96, 66, 66, 179, 255, 255, 95, 30, 25, 107)

valid_position_counter = 0
valid_position_history = []
invalid_position_history = []

loop_time = time.time()

wincap.start()

while(keyboard.is_pressed('q') == False):
    valid_positions = []
    closest_pixel = []
    already_visited = []
    time.sleep(2)

    # pre-process the image
    screenshot = wincap.get_screenshot()
    processed_image = vision_map.apply_hsv_filter(screenshot, hsv_map_filter)
    cv.cvtColor(processed_image, cv.COLOR_BGR2HSV)

    portal = vision_map_portal.findObjects(screenshot, 0.4, 1)
    output_image = vision_map_portal.draw_rectangles(screenshot, portal)
    cv.imshow('portal', output_image)

    # center_x = int(wincap.w / 2)
    # center_y = int(wincap.h / 2)
    # center = (center_x, center_y)
    # screen_center = wincap.get_screen_position((center_x, center_y))
    

    # blobDetectorParameters = cv.SimpleBlobDetector_Params()
    # blobDetectorParameters.filterByArea = True
    # blobDetectorParameters.minArea = 300
    # blobDetectorParameters.maxArea = 9999999
    # blobDetectorParameters.minDistBetweenBlobs = 0
    # blobDetectorParameters.filterByCircularity = False
    # blobDetectorParameters.filterByColor = False
    # blobDetectorParameters.filterByInertia = False
    # blobDetectorParameters.filterByConvexity = False

    # ######ITEM DETECTION#######
    # lower_item = np.array([0, 0, 0], dtype= 'uint8')
    # upper_item = np.array([0, 0, 0], dtype='uint8')
    # mask_item = cv.inRange(screenshot, lower_item, upper_item)
    # mask_item_inv = cv.bitwise_not(mask_item)
    
    # item_detector = cv.SimpleBlobDetector_create(blobDetectorParameters)
    # item_keypoints = item_detector.detect(mask_item)
    # itemImageWithKeypoints = cv.drawKeypoints(mask_item, item_keypoints, np.array([]), (0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # valid_items = []
    # for x in item_keypoints:
    #     valid_items.append([int(x.pt[0]), int(x.pt[1])])

    # if any(valid_items):
    #     closest_item = Utils.getClosestPixelToCenter(valid_items, center)
    #     closest_item = wincap.get_screen_position((closest_item[0], closest_item[1]))
    #     pyautogui.click(x = closest_item[0], y = closest_item[1])
    #     time.sleep(2)
    #     print('Picked up item')

    # #### MAP DETECTION ####
    # blobDetectorParameters.minArea = 50
    # blobDetectorParameters.filterByInertia = True
    # blobDetectorParameters.minInertiaRatio = 0
    # blobDetectorParameters.maxInertiaRatio = 0.5
    # blobDetectorParameters.filterByConvexity = False
    # blobDetectorParameters.filterByCircularity = False

    # lower = np.array([80, 65, 10], dtype= 'uint8')
    # upper = np.array([120, 90, 70], dtype='uint8')
    # mask = cv.inRange(processed_image, lower, upper)
    
    # map_detector = cv.SimpleBlobDetector_create(blobDetectorParameters)
    # keypoints = map_detector.detect(mask)
    # imageWithKeypoints = cv.drawKeypoints(mask, keypoints, np.array([]), (0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # ########################

    # valid_positions = []
    # for x in keypoints:
    #     valid_positions.append([int(x.pt[0]), int(x.pt[1])])

    # closest_pixel = Utils.getClosestPixelToCenter(valid_positions, center)

    # # Check if stuck every 4 loops and attempt different location if so
    # valid_position_history.append(closest_pixel)
    # valid_position_counter += 1
    # if valid_position_counter > 3:
    #     is_stuck = Utils.checkStuckInLocation(closest_pixel, valid_position_history)
    #     if is_stuck:
    #         invalid_position_history.append(closest_pixel)
    #         for x  in invalid_position_history:
    #             try:
    #                 valid_positions.remove(x)
    #             except ValueError:
    #                 pass
    #         closest_pixel = Utils.getClosestPixelToCenter(valid_positions, center)
    #         print('Tried UNSTUCK')
    #         print(invalid_position_history)
    #     valid_position_counter = 0
    #     valid_position_history = []

    # closest_pixel = wincap.get_screen_position((closest_pixel[0], closest_pixel[1]))

    # # keyboard actions
    # pyautogui.moveTo(x = closest_pixel[0], y = closest_pixel[1])
    # pyautogui.mouseDown()
    # time.sleep(1.9)
    # pyautogui.mouseUp()

    # cv.imshow("Keypoints", imageWithKeypoints)
    # cv.imshow("Item Keypoints", itemImageWithKeypoints)
    
    # # cv.imshow('Processed', processed_image)
    # # cv.imshow('mask', mask)

    # debug the loop rate
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')