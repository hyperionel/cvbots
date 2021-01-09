import cv2 as cv
import numpy as np
import os
import keyboard
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
while keyboard.is_pressed('q') == False:

    # get an updated image of the game
    screenshot = wincap.get_screenshot()

    # pre-process the image
    processed_image = vision_map.apply_hsv_filter(screenshot, hsv_map_filter)

    # do edge detection
    edges_image = vision_map.apply_edge_filter(processed_image)

    # do object detection
    #rectangles = vision_limestone.find(processed_image, 0.46)

    # draw the detection results onto the original image
    #output_image = vision_limestone.draw_rectangles(screenshot, rectangles)

    # keypoint searching
    keypoint_image = edges_image
    # crop the image to remove the ui elements
    x, w, y, h = [200, 1130, 70, 750]
    keypoint_image = keypoint_image[y:y+h, x:x+w]

    kp1, kp2, matches, match_points = vision_map.match_keypoints(keypoint_image)
    match_image = cv.drawMatches(
        vision_map.needle_img, 
        kp1, 
        keypoint_image, 
        kp2, 
        matches, 
        None)

    if match_points:
        # find the center point of all the matched features
        center_point = vision_map.centeroid(match_points)
        # account for the width of the needle image that appears on the left
        center_point[0] += vision_map.needle_w
        # drawn the found center point on the output image
        match_image = vision_map.draw_crosshairs(match_image, [center_point])

    # display the processed image
    # cv.imshow('Keypoint Search', match_image)
    cv.imshow('Processed', processed_image)
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









# FOG OF WAR
# X:  649 Y:  534 RGB: ( 12,  74, 106)
# X:  661 Y:  542 RGB: ( 12,  76, 108)
# X:  663 Y:  562 RGB: ( 12,  76, 108)
# X:  663 Y:  588 RGB: ( 12,  71, 105)
# X:  672 Y:  618 RGB: ( 12,  75, 107)
# X:  684 Y:  661 RGB: ( 12,  70, 104)
# X:  683 Y:  693 RGB: ( 12,  75, 107)
# X:  681 Y:  721 RGB: ( 12,  76, 109)
# X:  693 Y:  742 RGB: ( 12,  73, 108)
# X:  705 Y:  768 RGB: ( 24,  70, 101)
# X:  714 Y:  796 RGB: ( 12,  73, 109)
# X:  720 Y:  827 RGB: ( 12,  73, 109)
# X:  730 Y:  860 RGB: ( 12,  69, 108)
# X:  737 Y:  870 RGB: ( 12,  74, 110)
# X:  724 Y:  877 RGB: ( 31,  52,  77)
# X:  721 Y:  878 RGB: ( 31,  52,  77)
# X:  737 Y:  867 RGB: ( 12,  74, 110)
# X:  748 Y:  867 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  743 Y:  864 RGB: ( 13,  79, 112)
# X:  719 Y:  791 RGB: ( 16,  75, 109)
# X:  689 Y:  741 RGB: ( 12,  73, 108)
# X:  669 Y:  693 RGB: ( 12,  75, 107)
# X:  668 Y:  613 RGB: ( 12,  76, 108)
# X:  673 Y:  575 RGB: ( 12,  68, 100)
# X:  663 Y:  550 RGB: ( 12,  76, 108)
# X:  651 Y:  506 RGB: ( 12,  76, 108)
# X:  652 Y:  475 RGB: ( 12,  76, 108)
# X:  654 Y:  418 RGB: ( 12,  69, 103)
# X:  654 Y:  371 RGB: ( 16,  69, 100)
# X:  656 Y:  336 RGB: ( 11,  68, 102)
# X:  662 Y:  305 RGB: ( 12,  67,  99)
# X:  677 Y:  252 RGB: ( 14,  68,  99)
# X:  682 Y:  236 RGB: ( 19,  67,  95)
# X:  682 Y:  229 RGB: ( 19,  69,  99)

# MAP LIMIT
# X:  765 Y:  291 RGB: ( 45,  45,  92)
# X:  769 Y:  295 RGB: ( 47,  47,  93)
# X:  790 Y:  312 RGB: ( 52,  51, 101)
# X:  816 Y:  329 RGB: ( 53,  52, 107)
# X:  838 Y:  343 RGB: ( 46,  44,  93)
# X:  856 Y:  364 RGB: ( 54,  52, 108)
# X:  874 Y:  379 RGB: ( 53,  55, 110)
# X:  892 Y:  393 RGB: ( 55,  55, 111)
# X:  908 Y:  405 RGB: ( 52,  52, 109)
# X:  929 Y:  420 RGB: ( 52,  54, 110)
# X:  945 Y:  430 RGB: ( 47,  49,  99)
# X:  957 Y:  436 RGB: ( 50,  52, 107)
# X:  978 Y:  456 RGB: ( 47,  47,  97)
# X:  990 Y:  467 RGB: ( 52,  53, 108)
# X: 1003 Y:  476 RGB: ( 52,  56, 108)
# X: 1017 Y:  488 RGB: ( 48,  52,  96)
# X: 1023 Y:  495 RGB: ( 54,  59, 109)
# X: 1023 Y:  495 RGB: ( 54,  59, 109)