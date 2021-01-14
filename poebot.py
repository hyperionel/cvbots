import cv2 as cv
import pyautogui
import time
import Utils
from threading import Thread, Lock
from math import sqrt

class PoeBotState:
    INITIALIZING = 0
    SEARCHING_LOOT = 1
    SEARCHING = 2
    MOVING = 3
    LOOTING = 4

class PoeBot:

    #constants
    INITIALIZING_SECONDS = 3
    ATTEMPT_UNSTUCK_COUNT = 3

    #threading properties
    stopped = True
    lock = None

    #properties
    state = None
    map_targets = []
    map_target_history = []
    map_history_counter = 0
    map_invalid_target_history = []
    loot_targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    portal_tooltip = None
    waypoint_tooltip = None
    act_tooltip = None
    map_tooltip = None
    center = (0, 0)

    def __init__(self, window_offset, window_size):
        #create thread lock
        self.lock = Lock()

        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        int_w = int(self.window_w)
        int_h = int(self.window_h)
        self.center = (int_w, int_h)

        self.waypoint_tooltip = ''
        self.portal_tooltip = ''
        self.act_tooltip = ''

        self.state = PoeBotState.INITIALIZING
        self.timestamp = time()

    def map_move_to_target(self):
        target = self.map_find_next_target()
        pyautogui.moveTo(x = target[0], y = target[1])
        pyautogui.mouseDown()
        time.sleep(1.9)
        pyautogui.mouseUp()
        return True

    def map_find_next_target(self):
        next_target = Utils.getClosestPixelToCenter(self.map_targets, self.center)
        self.map_target_history.append(next_target)

        if self.map_move_is_stuck(next_target):
            self.attempt_unstuck(next_target)
            next_target = Utils.getClosestPixelToCenter(self.map_targets, self.center)
            self.map_target_history = []
            self.map_history_counter = 0

        next_target = self.get_screen_position((next_target[0], next_target[1]))
        return next_target

    def map_move_is_stuck(self, next_target):
        self.map_history_counter += 1
        if self.map_history_counter > PoeBot.ATTEMPT_UNSTUCK_COUNT:
            return not any(x != next_target for x in self.map_target_history)

    def attempt_unstuck(self, next_target):
        self.map_invalid_target_history.append()
        for x in self.map_invalid_target_history:
            try:
                self.map_targets.remove(x)
            except ValueError:
                pass

    def search_loot(self):
        closest_item = Utils.getClosestPixelToCenter(self.loot_targets, self.center)
        closest_item = self.get_screen_position(closest_item)
        pyautogui.click(x = closest_item[0], y = closest_item[1])
        time.sleep(2)
        print('Picked up item')
        
        return closest_item

    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def update_map_targets(self, targets):
        self.lock.acquire()
        self.map_targets = targets
        self.lock.release()
    
    def update_loot_targets(self, targets):
        self.lock.acquire()
        self.map_targets = targets
        self.lock.release()
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
    
    def run(self):
        while not self.stopped:
            if self.state == PoeBotState.INITIALIZING:
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = PoeBotState.SEARCHING_LOOT
                    self.lock.release()
            elif self.state == PoeBotState.SEARCHING_LOOT:
                loot_found = self.search_loot()
                if loot_found:
                    self.lock.acquire()
                    self.state = PoeBotState.LOOTING
                    self.lock.release()
            elif self.state == PoeBotState.SEARCHING:
                success = self.map_move_to_target()
                if success:
                    self.lock.acquire()
                    self.state = PoeBotState.MOVING
                    self.lock.release()
                else:
                    pass