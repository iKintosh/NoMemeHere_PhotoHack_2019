from imgen import ImageGenerator
from textdrawer import TextDrawer
from facedetector import FaceDetector
import colorgram

img = 'images/selfie1.jpg'
words = ['Я', 'сегодня', 'на', 'хакатоне', 'нафиг', 'и', 'тут', 'чертовски', 'весело', '!!!']

colors = colorgram.extract(img, 6)
colors = [col.rgb for col in colors]

fd = FaceDetector(img)
face_rect = fd.detect()

td = TextDrawer()
images = td.draw_random(words, fontfolder='fonts', fontsize=40, fontsize_delta=10, backcolor=colors, mode='corner', backcolor_mode='group')

ig = ImageGenerator(img)
x = ig.avoid_rect(face_rect, images)
ig.plot(x, save=True)