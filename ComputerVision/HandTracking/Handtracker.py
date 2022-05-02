import cv2
import mediapipe as mp
import pyautogui as pg

# Documentation: google.github.io/mediapipe/solutions/hands.html
# key press simulation: https://pyautogui.readthedocs.io/en/latest/

# Setting up camera
cap = cv2.VideoCapture(0)

# Declare hands object from mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)

# Use mpDraw to draw the key points
mpDraw = mp.solutions.drawing_utils

# Landmark numbers
Thumb = [1,2,3,4]
Index_finger = [5,6,7,8]
Middle_finger = [9,10,11,12]
Ring_finger = [13,14,15,16]
Pinky = [17,18,19,20]
Palm = [0,5,9,13,17]

def getHandCoord(handLandMarks, id):
    x = handLandMarks.landmark[mpHands.HandLandmark(id).value].x
    y = handLandMarks.landmark[mpHands.HandLandmark(id).value].y
    return x,y

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Hand detection + hand landmark marking
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for hand_no, handLms in enumerate(results.multi_hand_landmarks):

            # Thumbs up detection
            if (hand_no == 0):
                x4, y4 = getHandCoord(handLms, 4)
                x2, y2 = getHandCoord(handLms, 2)
    
                threshhold = 0.05
                if (y4<y2) and (abs(x2-x4)<threshhold):
                    cv2.putText(img,'Thumbs up', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                    pg.write('Nice ')
                elif (y4>y2) and (abs(x2-x4)<threshhold):
                    cv2.putText(img,'Thumbs down', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                    pg.write('Oof ')

            # for id, lm in enumerate(handLms.landmark):
            #     if id in Thumb: # Annotate part of hand
            #         h, w, c = img.shape
            #         cx, cy = int(lm.x *w), int(lm.y*h)
            #         cv2.circle(img, (cx,cy), 5, (0,0,255), -1)
                
            # Annotate whole hand
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): # the 'q' button is set as the quitting button
        print('break')
        cv2.destroyAllWindows()
        break
        