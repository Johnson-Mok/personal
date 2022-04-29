# https://faun.pub/virtual-keyboard-using-computer-vision-32b61981c5b1
# Documentation: google.github.io/mediapipe/solutions/hands.html
# key press simulation: https://pyautogui.readthedocs.io/en/latest/

import cv2
import mediapipe as mp
import pyautogui as pg
import numpy as np
import time
from pynput.keyboard import Controller

# Setting up camera
cap = cv2.VideoCapture(0)
w = 1280
h = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# Declare hands object from mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)

# Use mpDraw to draw the key points
mpDraw = mp.solutions.drawing_utils

def getHandCoord(handLandMarks, id):
    x = handLandMarks.landmark[mpHands.HandLandmark(id).value].x
    y = handLandMarks.landmark[mpHands.HandLandmark(id).value].y
    return x,y

# Landmark numbers
Index_finger_tip = 8

# Virtual keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
keyboard = Controller()

# Key sizes
start_h = int(h*0.75)
key_h = int(h*0.25/3)
key_w = int(w/10)

# Letter pos relative to box
letter_w = int(np.ceil(key_w*0.25))
letter_h = int(np.ceil(key_h*0.8))

# Save button startpoint
def getButtonPosList(key_w, key_h, start_h, keys):
        '''returns a list of tuples containing the startpoint of the key and the letter '''
        buttonPosList = []
        j = -1
        for ar in keys:
                j +=1
                i = 0
                for key in ar:
                        startpoint = (key_w*i,     start_h + key_h*j)
                        tup = (startpoint, key)
                        buttonPosList.append(tup)
                        i +=1
        return buttonPosList

buttonPosList = getButtonPosList(key_w, key_h, start_h, keys)

# Draw keyboard
def drawVirtualKeyboard(img, keys, key_w, key_h, start_h):
        '''Takes an image and key information to draw a virtual keyboard'''
        j = -1
        for ar in keys:
                j +=1
                i = 0
                for key in ar:
                        # Draw boxes for keyboard
                        startpoint = (key_w*i,     start_h + key_h*j)
                        endpoint   = (key_w*(i+1), start_h + key_h*(j+1))
                        colour = (255, 0, 0)
                        thick = -1
                        colourBorder = (255,255,255)
                        thickBorder = 1
                        cv2.rectangle(img, startpoint, endpoint, colour, thick)
                        cv2.rectangle(img, startpoint, endpoint, colourBorder, thickBorder) # Border

                        # Draw letter 
                        org = ( letter_w+key_w*i, letter_h + start_h + key_h*j )
                        fontLetter = cv2.FONT_HERSHEY_DUPLEX
                        fontSize = 1
                        fontColor = (255,255,255)
                        fontThick = 2
                        cv2.putText(img,key,org,fontLetter,fontSize,fontColor,fontThick)
                        
                        i +=1

while True:
        success, img = cap.read()
        img = cv2.flip(img,1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        drawVirtualKeyboard(img, keys, key_w, key_h, start_h)
        
        # Hand detection + hand landmark marking
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
                for hand_no, handLms in enumerate(results.multi_hand_landmarks):
                        # mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                        for id, lm in enumerate(handLms.landmark):
                                if id == Index_finger_tip: # Annotate part of hand
                                        cx, cy = int(lm.x *w), int(lm.y*h)
                                        cv2.circle(img, (cx,cy), 10, (0,0,255), -1)

                                        # Button pressing (WIP!!!!)
                                        for pos, letter in buttonPosList:
                                                condition = (pos[0] < cx < pos[0]+ key_w) & (pos[1] < cy < pos[1]+ key_h)
                                                if condition:
                                                        letterStart = letter
                                                        print('start',letterStart)
                                                        startTime = time.time()
                                                        
                                                        if ((time.time()-startTime > 2) & (letterStart == letterEnd)):
                                                                letterEnd = letter
                                                                print('end',letterEnd)
                                                                print('time',(time.time()-startTime > 2))           
                                                                print(letter)
                                                                
                                                                

        # Display camera image
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): # the 'q' button is set as the quitting button
                print('break')
                cv2.destroyAllWindows()
                break