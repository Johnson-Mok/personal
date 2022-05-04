import cv2
import time
import ctypes
import pyautogui as pg

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
def drawVirtualKeyboard(img, key_w, key_h, buttonPosList, letter_w, letter_h):
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
def pressAfterXSeconds(img, letter, waitSec, newRun, startTime, letterStart):
  '''
  Write the letter after maintaining position for X seconds.
  Need to put the output back into the function and define the start variables.

  Parameters
  ----------
  img: numpy.array
    Image to draw on.
  letter: str
    Letter currently selected by the user.
  waitSec: int
    Number of seconds to maintain the hold.
  newRun: bool
    Determines whether a new key is being selected.
  startTime: float
    Start time of the key being held.
  letterStart: str
    The letter being held.

  Returns
  ----------
  newRun: bool
    Determines whether a new key is being selected.
  startTime: float
    Start time of the key being held.
  letterStart: str
    The letter being held.
  '''

  if (newRun): # Start counting if condition satisfied
          letterStart = letter
          startTime = time.time()
          newRun = False
  elif ((time.time()-startTime >= waitSec) & (letterStart == letter) & ~newRun): # if more than 2 seconds, write
          print(letter)
          pg.press(letter) # Actual write, open a text document to see output
          newRun = True
  elif ((time.time()-startTime < waitSec) & (letterStart == letter) & ~newRun): # if less than 2 seconds, wait
          cv2.putText(img, f'{time.time()-startTime:.2f}', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3) # Show hold timer
  elif ((letterStart != letter) & ~newRun): # if index finger on different key, restart timer
          newRun = True

  return newRun, startTime, letterStart

def CAPSLOCK_STATE():
  '''
  Returns the state of capslock.
  Capslock on -> value not equal to zero.
  Capslock off -> value equal to zero.
  '''
  hllDll = ctypes.WinDLL ("User32.dll")
  VK_CAPITAL = 0x14
  return hllDll.GetKeyState(VK_CAPITAL)