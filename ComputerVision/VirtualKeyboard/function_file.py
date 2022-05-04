import cv2
import time
import ctypes
import pyautogui as pg

# Save button startpoint
def get_button_pos_list(key_w, key_h, start_h, keys):
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
  button_pos_list: list
        List of tuples containing the startpoint of the key and the letter.
  '''

  button_pos_list = []
  j = -1
  for ar in keys:
          j +=1
          i = 0
          for key in ar:
                  startpoint = (key_w*i,     start_h + key_h*j)
                  tup = (startpoint, key)
                  button_pos_list.append(tup)
                  i +=1
  return button_pos_list

def draw_key(img, key, pos, key_w, key_h, letter_w, letter_h):
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
  colour_border = (255,255,255)
  thick_border = 1
  cv2.rectangle(img, startpoint, endpoint, colour, thick)
  cv2.rectangle(img, startpoint, endpoint, colour_border, thick_border) # Border

  # Draw letter 
  org = (letter_w+pos[0], letter_h+pos[1])
  font_letter = cv2.FONT_HERSHEY_DUPLEX
  font_size = 1
  font_color = (255,255,255)
  font_thick = 2
  cv2.putText(img,key,org,font_letter,font_size,font_color,font_thick)

# Draw keyboard
def draw_virtual_keyboard(img, key_w, key_h, button_pos_list, letter_w, letter_h):
  '''Draws a virtual keyboard on the bottom of your image
  
  Parameters
  ----------
  img: numpy.ndarray
          Image to draw on.
  key_w: int
          Key box width.
  key_h: int
          Key box heigth.
  button_pos_list: list
          List of tuples containing button position and the letter itself.
  '''
  for pos,key in button_pos_list:
          draw_key(img, key, pos, key_w, key_h, letter_w, letter_h)

# Button press after x seconds
def press_after_x_seconds(img, letter, wait_sec, new_run, start_time, letter_start):
  '''
  Write the letter after maintaining position for X seconds.
  Need to put the output back into the function and define the start variables.

  Parameters
  ----------
  img: numpy.array
    Image to draw on.
  letter: str
    Letter currently selected by the user.
  wait_sec: int
    Number of seconds to maintain the hold.
  new_run: bool
    Determines whether a new key is being selected.
  start_time: float
    Start time of the key being held.
  letter_start: str
    The letter being held.

  Returns
  ----------
  new_run: bool
    Determines whether a new key is being selected.
  start_time: float
    Start time of the key being held.
  letter_start: str
    The letter being held.
  '''

  if (new_run): # Start counting if condition satisfied
          letter_start = letter
          start_time = time.time()
          new_run = False
  elif ((time.time()-start_time >= wait_sec) & (letter_start == letter) & ~new_run): # if more than 2 seconds, write
          print(letter)
          pg.press(letter) # Actual write, open a text document to see output
          new_run = True
  elif ((time.time()-start_time < wait_sec) & (letter_start == letter) & ~new_run): # if less than 2 seconds, wait
          cv2.putText(img, f'{time.time()-start_time:.2f}', (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3) # Show hold timer
  elif ((letter_start != letter) & ~new_run): # if index finger on different key, restart timer
          new_run = True

  return new_run, start_time, letter_start

def CAPSLOCK_STATE():
  '''
  Returns the state of capslock.
  Capslock on -> value not equal to zero.
  Capslock off -> value equal to zero.
  '''
  hllDll = ctypes.WinDLL ("User32.dll")
  VK_CAPITAL = 0x14
  return hllDll.GetKeyState(VK_CAPITAL)