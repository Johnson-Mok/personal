'''
Summary:
        Virtual keyboard making use of computer vision, OpenCV, and handtracking via mediapipe.
Sources:
        Inspiration: https://faun.pub/virtual-keyboard-using-computer-vision-32b61981c5b1
        Documentation handtracker: google.github.io/mediapipe/solutions/hands.html
        Key press simulation: https://pyautogui.readthedocs.io/en/latest/
        Source caps lock status: https://localcoder.org/python-3-detect-caps-lock-status

Usage:
        Make sure to set the right camera input. Default should be 0. Set to 1 if you have both a laptop cam and an external webcam.
        Press escape when you want to shut down the script.

Author: 
        JM
'''
# Import packages
import cv2
import mediapipe as mp
import pyautogui as pg
import numpy as np
from function_file import *

# Setting up camera
camerainput = 0 # default 0
cap = cv2.VideoCapture(camerainput)
w = 1280
h = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# Declare hands object from mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)

# Landmark numbers
index_finger_tip = 8

# Virtual keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P","capslock"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";","enter"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/","space"]]

# Key sizes as a function of the camera window
start_h = int(h*0.75)
key_h = int(h*0.25/3)
key_w = int(w/len(keys[0]))

# Letter position relative to box
letter_w = int(np.ceil(key_w*0.25))
letter_h = int(np.ceil(key_h*0.8))

# Set up for pressAfterXSeconds
new_run = True
start_time = 0
letter_start = 'Q'

button_pos_list = get_button_pos_list(key_w, key_h, start_h, keys)
pg.press("capslock") # start with lower letters

while True:
        success, img = cap.read()
        img = cv2.flip(img,1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        draw_virtual_keyboard(img, key_w, key_h, button_pos_list, letter_w, letter_h)

        # Show caps lock status
        CAPSLOCK = CAPSLOCK_STATE()
        if ((CAPSLOCK) & 0xffff) != 0:
                cv2.putText(img, "Lower", (int(w*0.8),70), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 3) 
        elif ((CAPSLOCK) & 0xffff) == 0:
                cv2.putText(img, "Upper", (int(w*0.8),70), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 3) 

        # Hand detection + hand landmark markingG
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
                for hand_no, hand_lms in enumerate(results.multi_hand_landmarks):
                        for id, lm in enumerate(hand_lms.landmark):
                                if id == index_finger_tip: # Annotate part of hand
                                        cx, cy = int(lm.x *w), int(lm.y*h)
                                        cv2.circle(img, (cx,cy), 10, (0,0,255), -1)

                                        # Button pressing (selects after maintaining the buttonpress for 2 seconds)
                                        for pos, letter in button_pos_list:
                                                condition = (pos[0] < cx < pos[0]+ key_w) & (pos[1] < cy < pos[1]+ key_h) # Index finger within a key box
                                                if condition:
                                                        new_run, start_time, letter_start = press_after_x_seconds(img, letter, 2, new_run, start_time, letter_start) # Hold for 2 seconds to write
                                                                
        # Display camera image
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == 27: #escape is set as the quitting button
                print('break')
                if ((CAPSLOCK) & 0xffff) != 0:
                        pg.press("capslock") # Turn caps lock of when shutting down.

                cv2.destroyAllWindows()
                break