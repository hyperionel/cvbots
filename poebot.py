import cv2 as cv
import pyautogui
from time import time, sleep
from utils import Utils
from threading import Thread, Lock
from math import sqrt

class PoeBotState:
    INITIALIZING = 1
    SEARCHING = 2
    PORTING_BACK = 3
    FINDING_WAYPOINT = 4
    NEXT_DESTINATION = 5

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
    map_target_history = []
    map_history_counter = 0
    map_invalid_target_history = []
    map_unstuck_attempts_count = 0
    center = (0, 0)
    port_back = False
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0

    #threading updates
    loot_targets = []
    map_targets = []
    waypoint_target = []
    waypoint_tooltip_target = []
    act_target = []
    node_target = []

    def __init__(self, window_offset, window_size):
        #create thread lock
        self.lock = Lock()

        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        int_w = int(self.window_w / 2)
        int_h = int(self.window_h / 2)
        self.center = (int_w, int_h)

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
            
            if self.should_port_back():
                self.port_back = True
                self.map_unstuck_attempts_count = 0
                
        next_target = self.get_screen_position((next_target[0], next_target[1]))
        return next_target

    def should_port_back(self):
        self.map_unstuck_attempts_count += 1
        return self.map_unstuck_attempts_count > PoeBot.PORT_BACK_COUNT

    def map_move_is_stuck(self, next_target):
        self.map_history_counter += 1
        if self.map_history_counter > PoeBot.ATTEMPT_UNSTUCK_COUNT:
            attempted_same_target =  not any(x != next_target for x in self.map_target_history)
            self.map_target_history = []
            self.map_history_counter = 0
            return attempted_same_target

    def attempt_unstuck(self, next_target):
        self.map_invalid_target_history.append(next_target)
        for x in self.map_invalid_target_history:
            try:
                self.map_targets.remove(x)
            except ValueError:
                pass

    def pickup_loot(self):
        closest_item = Utils.getClosestPixelToCenter(self.loot_targets, self.center)
        closest_item = self.get_screen_position(closest_item)
        
        pyautogui.click(x = closest_item[0], y = closest_item[1], clicks = 2)
        sleep(0.5)

    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def do_port_back(self):
        window_center = self.get_screen_position((self.center[0], self.center[1]))
        #adjust height for port location
        window_center = (window_center[0], window_center[1] - 100)
        
        pyautogui.click(x = window_center[0], y = window_center[1])
        pyautogui.press('T')
        sleep(2)
        pyautogui.click(x = window_center[0], y = window_center[1], clicks = 2)

    def move_to_waypoint(self):
        waypoint = self.get_screen_position(self.waypoint_target)
        pyautogui.click(x = waypoint[0], y = waypoint[1])

    def click_waypoint(self):
        waypoint = self.get_screen_position(self.waypoint_tooltip_target)
        pyautogui.click(x = waypoint[0], y = waypoint[1])

    def click_act(self):
        act = self.get_screen_position(self.act_target)
        pyautogui.click(x = act[0], y = act[1])

    def click_node(self):
        node = self.get_screen_position(self.node_target)
        pyautogui.click(x = node[0], y = node[1])

    def update_map_targets(self, targets):
        self.lock.acquire()
        self.map_targets = targets
        self.lock.release()
    
    def update_loot_targets(self, targets):
        self.lock.acquire()
        self.loot_targets = targets
        self.lock.release()

    def update_waypoint_target(self, target):
        self.lock.acquire()
        self.waypoint_target = target
        self.lock.release()

    def update_waypoint_tooltip_target(self, target):
        self.lock.acquire()
        self.waypoint_tooltip_target = target
        self.lock.release()

    def update_act_target(self, target):
        self.lock.acquire()
        self.act_target = target
        self.lock.release()

    def update_node_target(self, target):
        self.lock.acquire()
        self.node_target = target
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
                if True:
                    self.lock.acquire()
                    self.state = PoeBotState.PORTING_BACK
                    self.lock.release()
                elif any(self.loot_targets):
                    self.pickup_loot()
                elif any(self.map_targets):
                    self.map_move_to_target()
                else:
                    pass
            elif self.state == PoeBotState.PORTING_BACK:
                self.do_port_back()
                # sleep until the town loads
                sleep(15)
                #bring up the overlay map
                pyautogui.press('tab')
                self.lock.acquire()
                self.state = PoeBotState.FINDING_WAYPOINT
                self.lock.release()
            elif self.state == PoeBotState.FINDING_WAYPOINT:
                if any(self.act_target):
                    self.lock.acquire()
                    self.state = PoeBotState.NEXT_DESTINATION
                    self.lock.release()
                elif any(self.waypoint_tooltip_target):
                    self.click_waypoint()
                elif any(self.waypoint_target):
                    self.move_to_waypoint()
                else:
                    pass
            elif self.state == PoeBotState.NEXT_DESTINATION:
                if any(self.node_target):
                    self.click_node()
                elif any(self.act_target):
                    self.click_act()
                sleep(10)
                self.lock.acquire()
                self.state = PoeBotState.SEARCHING
                self.lock.release()
            else:
                pass

                

    def start_time(self):
        return time() > self.timestamp + self.INITIALIZING_SECONDS