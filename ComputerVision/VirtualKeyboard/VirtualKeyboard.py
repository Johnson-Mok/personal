# https://faun.pub/virtual-keyboard-using-computer-vision-32b61981c5b1
# Documentation: google.github.io/mediapipe/solutions/hands.html
# key press simulation: https://pyautogui.readthedocs.io/en/latest/

# Import packages
import cv2
import mediapipe as mp
import pyautogui as pg
import numpy as np
import time

# Setting up camera
camerainput = 1 # default 0
cap = cv2.VideoCapture(camerainput)
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

# Landmark numbers
Index_finger_tip = 8

# Virtual keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

# Key sizes as a function of the camera window
start_h = int(h*0.75)
key_h = int(h*0.25/3)
key_w = int(w/10)

# Letter position relative to box
letter_w = int(np.ceil(key_w*0.25))
letter_h = int(np.ceil(key_h*0.8))


### Helper functions
# Save button startpoint
def getButtonPosList(key_w, key_h, start_h, keys):
        '''Gets a list of tuples containing the startpoint of the key and the letter.
        
        Parameters
        ----------
        keys: list
                The letters to display ordered.
        key_w: int
                Key box width.
        key_h: int
                Key box heigth.
        start_h: int
                Start height of the whole keyboard.

        Returns
        ----------
        buttonPosList: list
             List of tuples containing the startpoint of the key and the letter.
        '''

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

def drawKey(img, key, pos, key_w, key_h, letter_w, letter_h):
        '''
        Function to draw a key button on the camera screen.

        Parameters
        ----------
        img: numpy.ndarray
                Image to draw on.
        key: str
                Letter to draw.
        pos: tuple
                Start position of the keybutton
        key_w: int
                Key box width.
        key_h
                Key box height.
        letter_w
                Letter width.
        letter_h
                Letter height.
        '''
        # Draw boxes for keyboard
        startpoint = (pos[0],        pos[1])
        endpoint   = (pos[0]+ key_w, pos[1]+ key_h)
        colour = (255, 0, 0)
        thick = -1
        colourBorder = (255,255,255)
        thickBorder = 1
        cv2.rectangle(img, startpoint, endpoint, colour, thick)
        cv2.rectangle(img, startpoint, endpoint, colourBorder, thickBorder) # Border

        # Draw letter 
        org = (letter_w+pos[0], letter_h+pos[1])
        fontLetter = cv2.FONT_HERSHEY_DUPLEX
        fontSize = 1
        fontColor = (255,255,255)
        fontThick = 2
        cv2.putText(img,key,org,fontLetter,fontSize,fontColor,fontThick)

# Draw keyboard
def drawVirtualKeyboard(img, key_w, key_h, buttonPosList):
        '''Draws a virtual keyboard on the bottom of your image
        
        Parameters
        ----------
        img: numpy.ndarray
                Image to draw on.
        key_w: int
                Key box width.
        key_h: int
                Key box heigth.
        buttonPosList: list
                List of tuples containing button position and the letter itself.
        '''
        for pos,key in buttonPosList:
                drawKey(img, key, pos, key_w, key_h, letter_w, letter_h)

# Button press after x seconds
def pressAfterXSeconds(letter, pos, key_w, key_h, waitSec):
        '''
        Write the letter after maintaining position for X seconds.

        Parameters
        ----------
        letter: str
                Letter currently selected by the user.
        waitSec: int
                Number of seconds to maintain the hold
        '''
        global newRun
        global startTime 
        global letterStart

        if (newRun): # Start counting if condition satisfied
                letterStart = letter
                startTime = time.time()
                newRun = False
        elif ((time.time()-startTime >= waitSec) & (letterStart == letter) & ~newRun): # if more than 2 seconds, write
                print(letter)
                pg.write(letter) # Actual write, open a text document to see output
                newRun = True
        elif ((time.time()-startTime < waitSec) & (letterStart == letter) & ~newRun): # if less than 2 seconds, wait
                cv2.putText(img, f'{time.time()-startTime:.2f}', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3) # Show hold timer
        elif ((letterStart != letter) & ~newRun): # if index finger on different key, restart timer
                newRun = True


### MAIN ###
# Set up for pressAfterXSeconds
newRun = True
startTime = 0
letterStart = 'Q'

buttonPosList = getButtonPosList(key_w, key_h, start_h, keys)

while True:
        success, img = cap.read()
        img = cv2.flip(img,1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        drawVirtualKeyboard(img, key_w, key_h, buttonPosList)
        
        # Hand detection + hand landmark markingG
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
                for hand_no, handLms in enumerate(results.multi_hand_landmarks):
                        # mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                        for id, lm in enumerate(handLms.landmark):
                                if id == Index_finger_tip: # Annotate part of hand
                                        cx, cy = int(lm.x *w), int(lm.y*h)
                                        cv2.circle(img, (cx,cy), 10, (0,0,255), -1)

                                        # Button pressing (selects after maintaining the buttonpress for 2 seconds)
                                        for pos, letter in buttonPosList:
                                                condition = (pos[0] < cx < pos[0]+ key_w) & (pos[1] < cy < pos[1]+ key_h) # Index finger within a key box
                                                if condition:
                                                        pressAfterXSeconds(letter, pos, key_w, key_h, 2) # Hold for 2 seconds to write
                                                                
        # Display camera image
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): # the 'q' button is set as the quitting button
                print('break')
                cv2.destroyAllWindows()
                break