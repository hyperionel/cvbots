import cv2 as cv
import pyautogui
from time import time, sleep
from utils import Utils
from threading import Thread, Lock
from math import sqrt

class PoeBotState:
    INITIALIZING = 0
    SEARCHING = 1
    PORTING_BACK = 2

class PoeBot:

    #constants
    INITIALIZING_SECONDS = 3
    ATTEMPT_UNSTUCK_COUNT = 3
    PORT_BACK_COUNT = 1

    #threading properties
    stopped = True
    lock = None

    #properties
    state = None
    map_targets = []
    map_target_history = []
    map_history_counter = 0
    map_invalid_target_history = []
    map_unstuck_attempts_history = []
    map_unstuck_attempts_count = 0
    loot_targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0

    center = (0, 0)
    port_back = False

    portal_tooltip = None
    waypoint_tooltip = None
    act_tooltip = None
    map_tooltip = None

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
        sleep(1.9)
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
            
            if self.should_port_back(next_target):
                self.port_back = True
                self.map_unstuck_attempts_history = []
                self.map_unstuck_attempts_count = 0
                
        next_target = self.get_screen_position((next_target[0], next_target[1]))
        return next_target

    def should_port_back(self, next_target):
        self.map_unstuck_attempts_history.append(next_target)
        self.map_unstuck_attempts_count += 1
        if self.map_unstuck_attempts_count > PoeBot.PORT_BACK_COUNT:
            return not any(x != next_target for x in self.map_unstuck_attempts_history)

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

    def pickup_loot(self):
        closest_item = Utils.getClosestPixelToCenter(self.loot_targets, self.center)
        closest_item = self.get_screen_position(closest_item)
        
        pyautogui.click(x = closest_item[0], y = closest_item[1], clicks = 2)
        sleep(2)
        print('Picked up item')

    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def update_map_targets(self, targets):
        self.lock.acquire()
        self.map_targets = targets
        self.lock.release()
    
    def update_loot_targets(self, targets):
        self.lock.acquire()
        self.loot_targets = targets
        self.lock.release()
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
    
    def run(self):
        while not self.stopped:
            sleep(0.5)
            if self.state == PoeBotState.INITIALIZING:
                if self.start_time():
                    self.lock.acquire()
                    self.state = PoeBotState.SEARCHING
                    self.lock.release()
            elif self.state == PoeBotState.SEARCHING:
                if self.port_back == True:
                    self.lock.acquire()
                    self.state = PoeBotState.PORTING_BACK
                    self.lock.release()
                elif any(self.loot_targets):
                    self.pickup_loot()
                elif any(self.map_targets):
                    self.map_move_to_target()
                else:
                    pass

    def start_time(self):
        return time() > self.timestamp + self.INITIALIZING_SECONDS