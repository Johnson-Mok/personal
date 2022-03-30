# Face recognizer 
# shout out to: https://github.com/informramiz/opencv-face-recognition-python

import cv2
import os
import numpy as np

# People that we are going to train on
subjects = ["", "Elvis Presley", "Barack Obama", "Mark Rutte", "Will Smith","Tom Cruise"]




###### Helper functions ######
# Function to resize image to below 500 in width and height
def image_downscale(image):
    max = 800
    width = image.shape[1]
    height = image.shape[0]
    if image.shape[1]>max:
        factor = max/image.shape[1]
        width = int(image.shape[1]*factor)
        height = int(image.shape[0]*factor)
    if image.shape[0]>max:
        factor = max/image.shape[0]
        width = int(image.shape[1]*factor)
        height = int(image.shape[0]*factor)
    image = cv2.resize(image, (width,height))
    return image

# Function to detect face using OpenCV
def detect_face(img, alg):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    PATH_opencv = os.path.join(PATH_ROOT, "opencv-files/")
    PATH_alg = ''
    if (alg == 'lbp'):
        PATH_alg = "lbpcascade_frontalface.xml"
    elif (alg == 'haar'):
        PATH_alg = "haarcascade_frontalface_alt.xml"
    PATH_cascade = os.path.join(PATH_opencv, PATH_alg)

    face_cascade = cv2.CascadeClassifier(PATH_cascade) # load OpenCV face detector, LBP: fast, Haar: accurate
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5); # detect multiscale images(some images may be closer to camera than others)
    
    #if no faces are detected then return original img
    if (len(faces) == 0):
        return None, None
    
    #under the assumption that there will be only one face,extract the face area
    (x, y, w, h) = faces[0]
    
    #return only the face part of the image
    return gray[y:y+w, x:x+h], faces[0]

# Read all persons' training images, 
# Detect face from each image
# Return two lists of exactly same size:
#   one list of faces and another list of labels for each face
def prepare_training_data(data_folder_path,alg):
    
    #Retrieve data
    dirs = os.listdir(data_folder_path)
    faces = []
    labels = []
    
    for dir_name in dirs:
        #subject directories start with letter 's'
        if not dir_name.startswith("s"):
            continue;
    
        # Get labels
        label = int(dir_name.replace("s", ""))
        subject_dir_path = data_folder_path + "/" + dir_name
        subject_images_names = os.listdir(subject_dir_path)
    
        #go through each image name, read image, 
        #detect face and add face to list of faces
        for image_name in subject_images_names:
            if image_name.startswith("."): #ignore system files like .DS_Store
                continue;
        
            image_path = subject_dir_path + "/" + image_name
            image = cv2.imread(image_path)
            
            # Resize images
            image = image_downscale(image)

            # cv2.imshow("Training on image...", image)
            # cv2.waitKey(100)
        
            #detect face
            face, rect = detect_face(image,alg)
        
            #Append labels and faces to list
            if face is not None:
                faces.append(face)
                labels.append(label)
    
    # cv2.destroyAllWindows()
    # cv2.waitKey(1)
    # cv2.destroyAllWindows()
    
    return faces, labels

# Function to draw rectangle on image 
def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
 
# Function to draw text on give image starting from passed (x, y) coordinates. 
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

# Recognize face and draw a rectangle around it
def predict_face(test_img,alg):
    img = test_img.copy()
    face, rect = detect_face(img,alg)
    label = face_recognizer.predict(face) # predict person label
    label_text = subjects[label[0]] #get name of respective label returned by face recognizer
    draw_rectangle(img, rect)
    draw_text(img, label_text, rect[0], rect[1]-5)
    return img, label_text

# Show test image with rectangle around face with name
def magic(photos):
    for photo in photos:
        print("Predicting images...")
        PATH_TEST = os.path.join(PATH_ROOT, "test-data")
        #load test images
        test_img = cv2.imread(os.path.join(PATH_TEST, photo))
        #perform a prediction
        predicted_img, label_text = predict_face(test_img,alg)
        print("Prediction complete, it's ",label_text)

        #display image
        predicted_img = image_downscale(predicted_img)
        cv2.imshow(photo, predicted_img)
        
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return 




###### Data preparation ######
alg = 'lbp' # lbp: faster, haar: more accurate

# Execute prepare training data
print("Preparing data...")
PATH_ROOT = os.path.dirname(os.path.realpath(__file__)) 
PATH_TRAIN = os.path.join(PATH_ROOT, "training-data")
faces, labels = prepare_training_data(PATH_TRAIN,alg)
print("Data prepared")

#print total faces and labels
print("Total faces: ", len(faces))
print("Total labels: ", len(labels))

###### Train Face Recognizer ######
face_recognizer = cv2.face.LBPHFaceRecognizer_create() 
# face_recognizer = cv2.face.EigenFaceRecognizer_create()
# face_recognizer = cv2.face.createFisherFaceRecognizer() 

face_recognizer.train(faces, np.array(labels))

###### Face prediction ######
PATH_TEST = os.path.join(PATH_ROOT, "test-data")
all_test = os.listdir(PATH_TEST)
magic(all_test) # magic(["test1.jpg"])


