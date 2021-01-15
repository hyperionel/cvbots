import cv2 as cv
import pyautogui
import numpy as np
from poebot import PoeBot, PoeBotState
from threading import Thread, Lock
from hsvfilter import HsvFilter
from vision import Vision
from time import sleep

class PoeDetector:

    #threading
    stopped = True
    lock = None

    #properties
    filter_screenshot = None
    screenshot = None
    loot_targets = []
    map_targets = []
    vision = None

    #screenshot filtering values
    map_filter_values = [96, 66, 66, 179, 255, 255, 95, 30, 25, 107]
    item_lower_range = [0, 0, 0]
    item_upper_range = [0, 0, 0]
    map_lower_range = [80, 65, 10]
    map_upper_range = [120, 90, 70]

    def __init__(self):
        self.vision = Vision()
        self.lock = Lock()

    def findSingleObject(self, haystack_img, needle_img, threshold = 0.9, method = cv.TM_CCOEFF_NORMED): 
        result = cv.matchTemplate(haystack_img, needle_img, method)

    def find_loot_targets(self):
        targets = self.findBlobs(self.screenshot, self.item_lower_range, self.item_upper_range, self.item_blob_params(), inverted=True)
        return targets

    def find_map_targets(self):
        filter_screenshot = self.vision.apply_hsv_filter(self.screenshot, self.map_filter())
        targets = self.findBlobs(filter_screenshot, self.map_lower_range, self.map_upper_range, self.map_blob_params())
        return targets

    def findBlobs(self, screenshot, lower_range, upper_range, blobParams, inverted=False, debug= False):
        cv.cvtColor(screenshot, cv.COLOR_BGR2HSV)
        lower_range = np.array(lower_range, dtype= 'uint8')
        upper_range = np.array(upper_range, dtype='uint8')
        mask_item = cv.inRange(screenshot, lower_range, upper_range)
        if inverted:
            cv.bitwise_not(mask_item)
        detector = cv.SimpleBlobDetector_create(blobParams)
        keypoints = detector.detect(mask_item)

        itemImageWithKeypoints = cv.drawKeypoints(mask_item, keypoints, np.array([]), (0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv.imshow('Current', itemImageWithKeypoints)

        valid_targets = []
        for x in keypoints:
            valid_targets.append([int(x.pt[0]), int(x.pt[1])])
        return valid_targets

    def item_blob_params(self):
        blobParams = cv.SimpleBlobDetector_Params()
        blobParams.filterByArea = True
        blobParams.minArea = 300
        blobParams.maxArea = 9999999
        blobParams.minDistBetweenBlobs = 0
        blobParams.filterByCircularity = False
        blobParams.filterByColor = False
        blobParams.filterByInertia = False
        blobParams.filterByConvexity = False
        return blobParams

    def map_blob_params(self):
        blobParams = cv.SimpleBlobDetector_Params()
        blobParams.filterByArea = True
        blobParams.maxArea = 9999999
        blobParams.minArea = 50
        blobParams.filterByInertia = True
        blobParams.minInertiaRatio = 0
        blobParams.maxInertiaRatio = 0.5
        blobParams.filterByConvexity = False
        blobParams.filterByCircularity = False
        blobParams.filterByColor = False
        return blobParams

    def map_filter(self):
        return HsvFilter(*self.map_filter_values)

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
    
    def stop(self):
        self.stopped = True

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()
    
    def run(self):
        while not self.stopped:
            sleep(0.5)
            if not self.screenshot is None:
                loot_targets = self.find_loot_targets()
                map_targets = self.find_map_targets()
                
                self.lock.acquire()
                self.loot_targets = loot_targets
                self.map_targets = map_targets
                self.lock.release()