import cv2
import face_recognition
import pickle
import os

def database_cr():
    faces_databse_path = 'faces_database'
    database_exist = os.path.exists(faces_databse_path)

    if database_exist :
        file_read = open('faces_database', 'rb')
        faces_database = pickle.load(file_read)

        file_read = open('names', 'rb')
        names = pickle.load(file_read)

    else :
        faces_database = []
        names = []

    return faces_database,names


def load_faces():
    file_read = open('faces_database', 'rb')
    faces_database = pickle.load(file_read)

    file_read = open('names', 'rb')
    names = pickle.load(file_read)


    return faces_database,names,


def capture_nearest_person(boxes):
    idx = boxes.index(max(boxes))
    return idx


def draw_rec(image,box):

    (top, right, bottom, left) = box
    start_pt = (left, top)
    end_pt = (right, bottom)
    color = (255, 0, 0)
    thickness = 2
    image = cv2.rectangle(image, start_pt, end_pt, color, thickness)

    return image


def face_detection(image):

    boxes = face_recognition.face_locations(image)
    # boxes = face_recognition.face_locations(image,model='cnn')

    if len(boxes)>0:
        idx = capture_nearest_person(boxes)
        box = boxes[idx]

        return box,idx
    else :
        return ()


def save_faces_database(faces_database,names):

    file_saving = open('faces_database', 'wb')
    pickle.dump(faces_database,file_saving)

    file_saving = open('names', 'wb')
    pickle.dump(names,file_saving)



def type_text_on_image(image, text):
    height,width,_ = image.shape
    start_x = 190
    start_y = 50
    start_pt =  (start_x,start_y)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (255, 0, 0)
    thickness = 2

    image = cv2.putText(image, str(text),start_pt , font,
                        fontScale, color, thickness, cv2.LINE_AA)
    return image



def visulize_identity(image, identity, box):

    (top, right, bottom, left) = box
    start_x = int(((right + left) / 2)-50)
    start_y = int(top - 10)
    start_pt =  (start_x,start_y)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (255, 0, 0)
    thickness = 2

    image = cv2.putText(image, str(identity),start_pt , font,
                        fontScale, color, thickness, cv2.LINE_AA)
    return image
