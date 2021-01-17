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
    RESET_NODE_AND_GO = 6

class PoeBot:

    #constants
    INITIALIZING_SECONDS = 3
    ATTEMPT_UNSTUCK_COUNT = 1
    PORT_BACK_COUNT = 1
    INVALID_LOOT_COUNT = 1
    INVALID_MAP_LOOT_COUNT = 1

    #threading properties
    stopped = True
    lock = None

    #properties
    state = None
    map_target_history = []
    map_history_counter = 0
    map_invalid_target_history = []
    map_unstuck_attempts_count = 0
    loot_history = []
    invalid_loot_history = []
    map_loot_history = []
    map_invalid_loot_history = []
    invalid_loot_count = 0
    map_invalid_loot_count = 0
    invalid_loot_unstuck_count = 0
    invalid_map_loot_unstuck_count = 0
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
    map_loot_targets = []
    waypoint_target = []
    waypoint_tooltip_target = []
    act_target = []
    node_target = []
    reset_tooltip_target = []

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
        sleep(2)
        pyautogui.mouseUp()
        return True

    def map_find_next_target(self):
        next_target = Utils.getClosestPixelToCenter(self.map_targets, self.center)

        if self.map_move_is_stuck(next_target):
            self.attempt_unstuck(next_target)
            next_target = Utils.getClosestPixelToCenter(self.map_targets, self.center)
            
            if self.should_port_back():
                self.port_back = True
                self.map_unstuck_attempts_count = 0
                
        coord = self.get_screen_position((next_target[0], next_target[1]))
        self.map_target_history.append([next_target[0], next_target[1]])
        return coord

    def should_port_back(self):
        return self.map_unstuck_attempts_count > PoeBot.PORT_BACK_COUNT

    def map_move_is_stuck(self, next_target):
        if any(self.map_target_history):
            attempted_same_target = not any(x != next_target for x in self.map_target_history[-1:])
            if attempted_same_target:
                self.map_history_counter += 1
                if self.map_history_counter > PoeBot.ATTEMPT_UNSTUCK_COUNT:
                    self.map_target_history = []
                    self.map_history_counter = 0
                    self.map_unstuck_attempts_count += 1
                return True
        return False

    def attempt_unstuck(self, next_target):
        self.map_invalid_target_history.append(next_target)
        for x in self.map_invalid_target_history:
            try:
                self.map_targets.remove(x)
            except ValueError:
                pass

    def pickup_loot(self):
        next_target = Utils.getClosestPixelToCenter(self.loot_targets, self.center)

        if self.pickup_loot_is_stuck(next_target):
            self.pickup_loot_attempt_unstuck(next_target)
            next_target = Utils.getClosestPixelToCenter(self.loot_targets, self.center)
            
            if self.pickup_loot_should_port_back():
                self.port_back = True
                self.invalid_loot_unstuck_count = 0

        coord = self.get_screen_position(next_target)

        pyautogui.click(x = coord[0], y = coord[1])
        sleep(2)
        self.loot_history.append([next_target[0], next_target[1]])
    
    def pickup_loot_should_port_back(self):
        return self.invalid_loot_unstuck_count > PoeBot.PORT_BACK_COUNT

    def pickup_loot_is_stuck(self, next_target):
        if any(self.loot_history):
            attempted_same_target =  not any(x != next_target for x in self.loot_history[-3:])
            if attempted_same_target:
                self.invalid_loot_count += 1
                if self.invalid_loot_count > PoeBot.INVALID_LOOT_COUNT:
                    self.loot_history = []
                    self.invalid_loot_count = 0
                    self.invalid_loot_unstuck_count += 1
                return True
        return False

    def pickup_loot_attempt_unstuck(self, next_target):
        self.invalid_loot_history.append(next_target)
        for x in self.invalid_loot_history:
            try:
                self.loot_targets.remove(x)
            except ValueError:
                pass

    def go_to_map_loot(self):
        next_target = Utils.getClosestPixelToCenter(self.map_loot_targets, self.center)

        if self.pickup_map_loot_is_stuck(next_target):
            self.pickup_map_loot_attempt_unstuck(next_target)
            next_target = Utils.getClosestPixelToCenter(self.map_loot_targets, self.center)
            
            if self.pickup_map_loot_should_port_back():
                self.port_back = True
                self.invalid_map_loot_unstuck_count = 0
                
        coord = self.get_screen_position(next_target)
        
        pyautogui.moveTo(x = coord[0], y = coord[1])
        pyautogui.mouseDown()
        sleep(2)
        pyautogui.mouseUp()
        self.map_loot_history.append([next_target[0], next_target[1]])
    
    def pickup_map_loot_should_port_back(self):
        return self.invalid_map_loot_unstuck_count > PoeBot.PORT_BACK_COUNT

    def pickup_map_loot_is_stuck(self, next_target):
        if not any(self.map_loot_history):
            attempted_same_target = not any(x != next_target for x in self.map_loot_history[-3:])
            if attempted_same_target:
                self.map_invalid_loot_count += 1
                if self.map_invalid_loot_count > PoeBot.INVALID_LOOT_COUNT:
                    self.map_loot_history = []
                    self.map_invalid_loot_count = 0
                    self.invalid_map_loot_unstuck_count += 1
                return True
        return False

    def pickup_map_loot_attempt_unstuck(self, next_target):
        self.map_invalid_loot_history.append(next_target)
        for x in self.map_invalid_loot_history:
            try:
                self.map_loot_targets.remove(x)
            except ValueError:
                pass

    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    def do_port_back(self):
        window_center = self.get_screen_position((self.center[0], self.center[1]))
        #adjust height for port location
        window_center = (window_center[0], window_center[1] - 100)
        
        pyautogui.click(x = window_center[0], y = window_center[1])
        pyautogui.press('T')
        sleep(4)
        pyautogui.click(x = window_center[0], y = window_center[1], clicks = 2)
        # sleep until the town loads
        sleep(15)
        #bring up the overlay map
        pyautogui.press('tab')

    def move_to_waypoint(self): 
        waypoint = self.get_screen_position(self.waypoint_target)
        pyautogui.click(x = waypoint[0], y = waypoint[1])

    def click_waypoint(self):
        waypoint = self.get_screen_position(self.waypoint_tooltip_target)
        adjusted_x = waypoint[0] + 15
        adjusted_y = waypoint[1] + 5
        pyautogui.moveTo(x = adjusted_x, y = adjusted_y)
        sleep(2)
        pyautogui.click(x = adjusted_x, y = adjusted_y)

    def click_act(self):
        act = self.get_screen_position(self.act_target)
        adjusted_x = act[0] + 20
        adjusted_y = act[1] + 10
        pyautogui.moveTo(x = adjusted_x, y = adjusted_y)
        sleep(2)
        pyautogui.click(x = adjusted_x, y = adjusted_y)

    def click_node(self):
        node = self.get_screen_position(self.node_target)
        adjusted_x = node[0] + 10
        adjusted_y = node[1] + 10
        pyautogui.moveTo(x = adjusted_x, y = adjusted_y)
        sleep(2)
        pyautogui.keyDown('ctrl')
        pyautogui.click(x = adjusted_x, y = adjusted_y)
        pyautogui.keyUp('ctrl')

    def click_reset_tooltip_target(self):
        reset_tooltip = self.get_screen_position(self.reset_tooltip_target)
        adjusted_x = reset_tooltip[0] + 10
        adjusted_y = reset_tooltip[1] + 10
        pyautogui.moveTo(x = adjusted_x, y = adjusted_y)
        sleep(2)
        pyautogui.click(x = adjusted_x, y = adjusted_y)
        sleep(10)
        pyautogui.press('tab')

    def update_map_targets(self, targets):
        self.lock.acquire()
        self.map_targets = targets
        self.lock.release()
    
    def update_loot_targets(self, targets):
        self.lock.acquire()
        self.loot_targets = targets
        self.lock.release()

    def update_map_loot_targets(self, targets):
        self.lock.acquire()
        self.map_loot_targets = targets
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

    def update_reset_tooltip_target(self, target):
        self.lock.acquire()
        self.reset_tooltip_target = target
        self.lock.release()
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.lock.acquire()
        self.stopped = True
        self.lock.release()
    
    def run(self):
        while not self.stopped:
            if self.state == PoeBotState.INITIALIZING:
                print('INITIALIZING')
                if self.start_time():
                    self.lock.acquire()
                    self.state = PoeBotState.SEARCHING
                    self.lock.release()
            elif self.state == PoeBotState.SEARCHING:
                if self.port_back:
                    self.lock.acquire()
                    self.state = PoeBotState.PORTING_BACK
                    self.lock.release()
                elif any(self.loot_targets):
                    print('LOOTING')
                    self.pickup_loot()
                elif any(self.map_loot_targets):
                    print('MOVING TO MAP LOOT')
                    self.go_to_map_loot()
                elif any(self.map_targets):
                    print('MOVING')
                    self.map_move_to_target()
                else:
                    pass
            elif self.state == PoeBotState.PORTING_BACK:
                print('PORT BACK')
                self.do_port_back()
                self.lock.acquire()
                self.state = PoeBotState.FINDING_WAYPOINT
                self.port_back = False
                self.lock.release()
            elif self.state == PoeBotState.FINDING_WAYPOINT:
                print('FINDING WAYPOINT')
                if any(self.waypoint_tooltip_target):
                    self.click_waypoint()
                    self.lock.acquire()
                    self.state = PoeBotState.NEXT_DESTINATION
                    self.lock.release()
                elif any(self.waypoint_target):
                    self.move_to_waypoint()
                else:
                    pass
            elif self.state == PoeBotState.NEXT_DESTINATION:
                print('SELECTING ACT & MAP')
                if any(self.node_target):
                    self.click_node()
                    self.lock.acquire()
                    self.state = PoeBotState.RESET_NODE_AND_GO
                    self.lock.release()
                elif any(self.act_target):
                    self.click_act()
                else:
                    pass
            elif self.state == PoeBotState.RESET_NODE_AND_GO:
                print('RESETTING')
                if any(self.reset_tooltip_target):
                    self.click_reset_tooltip_target()
                    self.lock.acquire()
                    self.state = PoeBotState.SEARCHING
                    self.lock.release()
                else:
                    pass
            else:
                pass

                

    def start_time(self):
        return time() > self.timestamp + self.INITIALIZING_SECONDS