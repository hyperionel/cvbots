import cv2 as cv
import numpy as np
import os
import keyboard
import pyautogui
from PIL import Image
from time import time
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

loop_time = time()
while True:

    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # pre-process the image
    processed_image = vision_map.apply_hsv_filter(screenshot, hsv_map_filter)

    # do edge detection
    # edges_image = vision_map.apply_edge_filter(processed_image)

    # do object detection
    #rectangles = vision_limestone.findObjects(processed_image, 0.46)

    # draw the detection results onto the original image
    #output_image = vision_limestone.draw_rectangles(screenshot, rectangles)

    # keypoint searching
    # keypoint_image = edges_image
    # crop the image to remove the ui elements
    # x, w, y, h = [200, 1130, 70, 750]
    # keypoint_image = keypoint_image[y:y+h, x:x+w]

    # kp1, kp2, matches, match_points = vision_map.match_keypoints(keypoint_image)
    # match_image = cv.drawMatches(
    #     vision_map.needle_img, 
    #     kp1, 
    #     keypoint_image, 
    #     kp2, 
    #     matches, 
    #     None)

    # if match_points:
    #     # find the center point of all the matched features
    #     center_point = vision_map.centeroid(match_points)
    #     # account for the width of the needle image that appears on the left
    #     center_point[0] += vision_map.needle_w
    #     # drawn the found center point on the output image
    #     match_image = vision_map.draw_crosshairs(match_image, [center_point])

    # display the processed image
    # cv.imshow('Keypoint Search', match_image)
    
    fog_range = range(10, 30)
    map_range = range(40, 60)
    
    image_object = Image.fromarray(processed_image)
    loaded_object = image_object.load()

    for x in range(0, 484, 4):
        for y in range(0, 462, 4):
            r, g, b = loaded_object[x, y]
            if r in fog_range:
                image_object.putpixel((x, y), (0, 255, 0))
            if r in map_range:
                image_object.putpixel((x, y), (255, 0, 0))
    
    image_object = np.array(image_object)
    image_object = image_object[:, :, ::-1].copy()

    cv.imshow('Processed', image_object)
    # cv.imshow('Edges', edges_image)
    #cv.imshow('Matches', output_image)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')