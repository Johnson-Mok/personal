## Facial recognition comparision between two images.
# Usage: 
# 1: Set take_picture to True/False
# If take_picture is set to True. Press 'q' to take the picture.

# Note: The number in the image is not the accuracy. It is the facial distance.
# The smaller the number, the larger the similarity.

# Import
import cv2
import face_recognition
from os.path import exists
import os

# Input #
PATH = os.path.dirname(os.path.realpath(__file__)) 
truthname='PF.jpeg' # Ground truth picture
savename='Catfishtest.jpg' # Picture taken to compare with the ground truth
take_picture = False # True/False
cam_channel = 1 # Default: 0. Use when you have multiple webcams, e.g., 0: laptop camera, 1: external camera

PATH_TRUTH = os.path.join(PATH, truthname)
PATH_TEST = os.path.join(PATH, savename)

# Picture taking
if(take_picture):
    vid = cv2.VideoCapture(cam_channel) 
    while(True):
        ret, frame = vid.read()
        cv2.imshow('frame', frame)
        cv2.imwrite(PATH_TEST, frame) # Saves frame as image
        if cv2.waitKey(1) & 0xFF == ord('q'): # the 'q' button is set as the quitting button
            print('break')
            break
    vid.release()
    cv2.destroyAllWindows()

# Compare with ground truth
if(exists(PATH_TEST)):
    # Retrieve images
    imgmain = face_recognition.load_image_file(PATH_TRUTH) 
    imgmain = cv2.cvtColor(imgmain, cv2.COLOR_BGR2RGB)
    imgTest = face_recognition.load_image_file(PATH_TEST) 
    imgTest = cv2.cvtColor(imgTest, cv2.COLOR_BGR2RGB)

    # Encode truth
    faceLoc = face_recognition.face_locations(imgmain)[0]
    encodeElon = face_recognition.face_encodings(imgmain)[0]
    cv2.rectangle(imgmain, (faceLoc[3], faceLoc[0]), (faceLoc[1], faceLoc[2]), (255, 0, 255), 2)

    # Encode capture
    faceLocTest = face_recognition.face_locations(imgTest)[0]
    encodeTest = face_recognition.face_encodings(imgTest)[0]
    cv2.rectangle(imgTest, (faceLocTest[3], faceLocTest[0]), (faceLocTest[1], faceLocTest[2]), (255, 0, 255), 2)

    # Results
    results = face_recognition.compare_faces([encodeElon], encodeTest, tolerance=0.5)
    faceDis = face_recognition.face_distance([encodeElon], encodeTest)
    print(results, faceDis)
    cv2.putText(imgTest, f'{results} {round(faceDis[0], 2)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Truth Image', imgmain)
    cv2.imshow('Test Image', imgTest)
    cv2.waitKey(0)
else:
    print('Test image not found')
