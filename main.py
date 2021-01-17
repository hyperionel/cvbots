from numpy.lib.polynomial import _polyder_dispatcher
from poebot import PoeBot
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
from hsvfilter import HsvFilter
from edgefilter import EdgeFilter
from utils import Utils
from poebot import PoeBot, PoeBotState
from poedetector import PoeDetector

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# initialize the WindowCapture class
wincap = WindowCapture('Path of Exile')

poedetector = PoeDetector()

bot = PoeBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

wincap.start()
poedetector.start_main_thread()
bot.start()

while(keyboard.is_pressed('q') == False):
    if keyboard.is_pressed('f1'):
        if wincap.stopped == False and poedetector.stopped == False and bot.stopped == False:
            wincap.stop()
            poedetector.stop()
            bot.stop()
            print('PAUSED BOT')
    
    if keyboard.is_pressed('f2'):
        if wincap.stopped == True and poedetector.stopped == True and bot.stopped == True:
            wincap.start()
            poedetector.start_main_thread()
            bot.start()
            print('RESUMED BOT')

    if keyboard.is_pressed('f3'):
        bot.state = PoeBotState.PORTING_BACK
        print('STARTED PORTBACK PHASE')

    if wincap.screenshot is None:
        continue

    screenshot = wincap.screenshot
    poedetector.update_screenshot(screenshot)

    if bot.state in range(0, 3):
        loot_targets = poedetector.loot_targets
        map_targets = poedetector.map_targets
        map_loot_targets = poedetector.map_loot_targets

        if bot.state == PoeBotState.INITIALIZING:
            poedetector.update_bot_state(bot.state)
            bot.update_loot_targets(loot_targets)
            bot.update_map_loot_targets(map_loot_targets)
            bot.update_map_targets(map_targets)
        if bot.state == PoeBotState.SEARCHING:
            poedetector.update_bot_state(bot.state)
            bot.update_loot_targets(loot_targets)
            bot.update_map_loot_targets(map_loot_targets)
            bot.update_map_targets(map_targets)
    elif bot.state == PoeBotState.PORTING_BACK:
        poedetector.update_bot_state(bot.state)
        pass
    elif bot.state == PoeBotState.FINDING_WAYPOINT:
        poedetector.update_bot_state(bot.state)
        bot.update_waypoint_target(poedetector.waypoint_target)
        bot.update_waypoint_tooltip_target(poedetector.waypoint_tooltip_target)
        bot.update_act_target(poedetector.act_target)
    elif bot.state == PoeBotState.NEXT_DESTINATION:
        poedetector.update_bot_state(bot.state)
        bot.update_act_target(poedetector.act_target)
        bot.update_node_target(poedetector.node_target)
    elif bot.state == PoeBotState.RESET_NODE_AND_GO:
        poedetector.update_bot_state(bot.state)
        bot.update_reset_tooltip_target(poedetector.reset_tooltip_target)
    else:
        pass

wincap.stop()
bot.stop()
poedetector.stop()
cv.destroyAllWindows()
print('Done.')