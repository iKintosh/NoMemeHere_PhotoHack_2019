from imgen import ImageGenerator
from textdrawer import TextDrawer
from is_list import isList

text = 'античный город, осень, серое небо, каменная дорога, деревья, карета с лошадьми, воины на лошадях'

result = isList(text)
td = TextDrawer()

if result:
    img = 'images/note.png'
    terms = [' '.join(s).replace(',', ' ') for s in result]

    images = td.draw_random(terms, fontfolder='listfonts', fontsize=30, fontsize_delta=0, font_mode='fixed',
                            backcolor_mode='fixed', mode='corner')
    ig = ImageGenerator(img)
    x = ig.create_celllist(images)
    ig.plot(x, save=True)
else:
    print('No list =(')