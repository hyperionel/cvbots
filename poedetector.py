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
    vision = None
    poe_bot_state = None

    #threading updates
    loot_targets = []
    map_targets = []
    waypoint_target = []
    waypoint_tooltip_target = []
    act_target = []
    node_target = []
    

    #screenshot filtering values
    map_filter_values = [96, 66, 66, 179, 255, 255, 95, 30, 25, 107]
    item_lower_range = [0, 0, 0]
    item_upper_range = [0, 0, 0]
    map_lower_range = [80, 65, 10]
    map_upper_range = [120, 90, 70]

    poe_waypoint_map_needle = 'poe_map_waypoint.png'
    poe_waypoint_map_tooltip = 'poe_waypoint_tooltip.png'
    poe_act_tooltip = 'act_tooltip.png'
    poe_node_tooltip = 'map_tooltip.png'

    def __init__(self):
        self.vision = Vision()
        self.lock = Lock()

    def findSingleObject(self, haystack_img, needle_img, threshold = 0.9, method = cv.TM_CCOEFF_NORMED): 
        needle_img = cv.imread(needle_img)
        results = cv.matchTemplate(haystack_img, needle_img, method)
        results  =  np.where(results >= threshold)
        results = list(zip(*results[::-1]))
        if not results:
            return np.array([], dtype=np.int32).reshape(0, 4)
        return results

    def find_map_waypoint(self):
        map_waypoint = self.findSingleObject(self.screenshot, self.poe_waypoint_map_needle)
        return map_waypoint
    
    def find_map_waypoint_tooltip(self):
        map_tooltip = self.findSingleObject(self.screenshot, self.poe_waypoint_map_tooltip)
        return map_tooltip

    def find_act_target(self):
        act_target = self.findSingleObject(self.screenshot, self.poe_act_tooltip)
        return act_target

    def find_node_target(self):
        node_target = self.findSingleObject(self.screenshot, self.poe_node_tooltip)
        return node_target

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
        blobParams.minArea = 20
        blobParams.filterByInertia = True
        blobParams.minInertiaRatio = 0
        blobParams.maxInertiaRatio = 0.1
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

    def update_bot_state(self, state):
        self.lock.acquire()
        self.poe_bot_state = state
        self.lock.release()
    
    def run(self):
        while not self.stopped:
            sleep(0.1)
            if not self.poe_bot_state is None:
                if self.poe_bot_state in range(0, 3):
                    if not self.screenshot is None:
                        loot_targets = self.find_loot_targets()
                        map_targets = self.find_map_targets()
                        
                        self.lock.acquire()
                        self.loot_targets = loot_targets
                        self.map_targets = map_targets
                        self.lock.release()
                elif self.poe_bot_state == PoeBotState.FINDING_WAYPOINT:
                    if not self.screenshot is None:
                        map_waypoint = self.find_map_waypoint()
                        map_waypoint_tooltip = self.find_map_waypoint_tooltip()
                        act_target = self.find_act_target()

                        self.lock.acquire()
                        self.waypoint_target = map_waypoint
                        self.waypoint_tooltip_target = map_waypoint_tooltip
                        self.act_target = act_target
                        self.lock.release()
                elif self.poe_bot_state == PoeBotState.NEXT_DESTINATION:
                    if not self.screenshot is None:
                        act_target = self.find_act_target()
                        node_target = self.find_node_target()

                        self.lock.acquire()
                        self.act_target = act_target
                        self.node_target = node_target
                        self.lock.release()
                else:
                    pass


