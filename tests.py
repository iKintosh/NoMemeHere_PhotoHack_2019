from imgen import ImageGenerator
from textdrawer import TextDrawer
from facedetector import FaceDetector
from timedetector import time_message_detect
import colorgram
from is_list import isList
import numpy as np



#text = 'античный город, осень, серое небо, каменная дорога, деревья, карета с лошадьми, воины на лошадях'
text = 'Гравитирующая сфера, не вдаваясь в подробности, вертикально вращает квазар. Фонон, как и везде в пределах наблюдаемой вселенной, синхронизует изоморфный лазер - все дальнейшее далеко выходит за рамки текущего исследования и не будет здесь рассматриваться.'

result = isList(text)
td = TextDrawer()
fontsize = 15

if result:
    img = 'images/note.png'
    terms = [' '.join(s).replace(',', ' ') for s in result]

    images = td.draw_random(terms, fontfolder='listfonts', fontsize=fontsize, fontsize_delta=0, font_mode='fixed',
                            backcolor_mode='fixed', mode='corner')
    ig = ImageGenerator(img)
    x = ig.create_celllist(images)
    ig.save(x, savepath='output/var1.png')
else:
    img = 'images/alarm.jpg'
    terms, mask = time_message_detect(message=text)

    if sum(mask) > 0:
        td = TextDrawer()
        images = td.draw_random(terms, fontfolder='fonts', fontsize=fontsize, fontsize_delta=0, font_mode='fixed',
                                backcolor_mode='fixed', mask=mask, mode='corner')

        ig = ImageGenerator(img)
        # x = ig.create_celllist(images)
        x = ig.avoid_rect((0, 0, 0, 0), images)
        ig.save(x, savepath='output/var1.png')



avatar = 'images/selfie1.jpg'

ig = ImageGenerator(avatar)
fd = FaceDetector(avatar)
try:
    face_rect = fd.detect()
except:
    s = 0.25
    w = ig.imgwidth()
    h = ig.imgheight()
    face_rect = ((w - s * w) // 2, (h - s * h) // 2, s * w, s * h )

td = TextDrawer()
images = td.draw_random(text.split(' '), fontfolder='fonts', fontsize=fontsize, fontsize_delta=10, mode='corner', backcolor_mode='random')
x = ig.avoid_rect(face_rect, images)
ig.save(x, savepath='output/var2.png')



colors = colorgram.extract(img, 6)
colors = [col.rgb for col in colors]

images = td.draw_random(text.split(' '), fontfolder='fonts', fontsize=fontsize, fontsize_delta=10, backcolor=colors, mode='corner', backcolor_mode='group')

x = ig.avoid_rect(face_rect, images)
ig.save(x, savepath='output/var3.png')







