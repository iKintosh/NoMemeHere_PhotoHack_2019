import cv2 as cv
from copy import deepcopy

class FaceDetector():
    def __init__(self, path_to_img):
        self.image = cv.imread(path_to_img)

    # img - opencv image
    def detect(self):
        face_detector = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        return faces[0]

    def draw_frame(self, rect, show=False):
        img = deepcopy(self.image)
        x = rect[0]
        y = rect[1]
        w = rect[2]
        h = rect[3]
        cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        if show:
            cv.imshow('img', img)
            cv.waitKey(0)
            cv.destroyAllWindows()
        return img

