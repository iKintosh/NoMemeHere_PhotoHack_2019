from imgen import ImageGenerator
from textdrawer import TextDrawer
from facedetector import FaceDetector
from timedetector import time_message_detect

img = 'images/note.png'

terms, mask = time_message_detect()

td = TextDrawer()
images = td.draw_random(terms, fontfolder='fonts', fontsize=50, fontsize_delta=0, font_mode='fixed',  backcolor_mode='fixed', mask=mask, mode='corner')

ig = ImageGenerator(img)
x = ig.create_celllist(images)
ig.plot(x, save=True)