from PIL import Image, ImageDraw, ImageFont, ImageChops
import numpy as np
import os
from copy import deepcopy

class TextDrawer():
    def get_text_size(self, text, fontname, fontsize):
        font = ImageFont.truetype(fontname, size=fontsize)
        return font.getsize(text)

    def trim(self, img):
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        return img.crop(bbox)

    def correct_color(self, col):
        change = 30
        luminance = 0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2]
        if luminance < 165:
            col = [c + change for c in col]
            col = [c if c < 256 else 255 for c in col]
        else:
            col = [c - change for c in col]
            col = [c if c >= 0 else 0 for c in col]
        return tuple(col)

    def trans_paste(self, fg_img, bg_img, alpha=1.0, box=(0, 0)):
        fg_img_trans = Image.new("RGBA", fg_img.size)
        fg_img_trans = Image.blend(fg_img_trans, fg_img, alpha)
        bg_img.paste(fg_img_trans, box, fg_img_trans)
        return bg_img

    def draw(self, text, fontname='arial', fontsize=20, save=False, savepath='text.png', backcolor=(255, 255, 255), textcolor=(0, 0, 0), mode='default'):
        if mode == 'default':
            delta = 5
            size = self.get_text_size(text, fontname=fontname, fontsize=fontsize)
            img = Image.new("RGBA", (size[0] + 2 * delta, size[1] + 2 * delta), backcolor)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(fontname, size=fontsize)
            draw.text((delta, delta), text, textcolor, font=font)
        elif mode == 'corner':
            delta = 20
            inner_img = self.draw(text, fontname=fontname, fontsize=fontsize, backcolor=backcolor, textcolor=textcolor)
            corners = [(0, 0), (inner_img.size[0] + delta, 0), (inner_img.size[0] + delta, inner_img.size[1] + delta), (0, inner_img.size[1] + delta)]
            points = []
            for corner in corners:
                x = np.random.randint(corner[0], corner[0] + delta)
                y = np.random.randint(corner[1], corner[1] + delta)
                points.append((x, y))
            img = Image.new("RGBA", (inner_img.size[0] + 2 * delta, inner_img.size[1] + 2 * delta), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.polygon(points, fill=backcolor)
            img = self.trans_paste(inner_img, img, alpha=1.0, box=(delta, delta))

        if save:
            img.save(savepath)
        return img



    def get_random_color(self):
        return tuple((255 * np.random.random(3)).astype(int))

    def get_second_random_color(self, col):
        luminance = 0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2]
        if luminance > 165:
            return (0, 0, 0)
        else:
            return (255, 255, 255)

    def draw_random(self, texts, fontfolder=None, fontsize=30, fontsize_delta=10,
                    save=False, savepath='text.png',
                    backcolor=None, textcolor=None,
                    font_mode='random', backcolor_mode='random',
                    mask=None, mode='default'):
        if fontfolder is None:
            fonts = ['arial']
        else:
            fonts = [fontfolder + '/' + f for f in os.listdir(fontfolder)]

        if mask is None:
            mask = [False] * len(texts)

        images = []
        fixed_index = np.random.randint(0, len(fonts))
        fixed_color = self.get_random_color()

        for i, text in enumerate(texts):
            if font_mode == 'random':
                index = np.random.randint(0, len(fonts))
                font = fonts[index]
            elif font_mode == 'fixed':
                font = fonts[fixed_index]

            if mask[i]:
                font_size = int(1.5 * (fontsize + np.random.randint(0, 2 * fontsize_delta + 1) - fontsize_delta))

                if textcolor is None:
                    if backcolor_mode == 'random':
                        tcolor = self.get_random_color()
                    elif backcolor_mode == 'fixed':
                        tcolor = fixed_color
                    elif backcolor_mode == 'group':
                        index = np.random.randint(0, len(backcolor))
                        tcolor = self.correct_color(backcolor[index])
                else:
                    tcolor = textcolor

                if backcolor is None:
                    bcolor = self.get_second_random_color(tcolor)
                else:
                    bcolor = backcolor
            else:
                font_size = fontsize + np.random.randint(0, 2 * fontsize_delta + 1) - fontsize_delta

                if backcolor is None:
                    if backcolor_mode == 'random':
                        bcolor = self.get_random_color()
                    elif backcolor_mode == 'fixed':
                        bcolor = fixed_color
                else:
                    if backcolor_mode == 'group':
                        index = np.random.randint(0, len(backcolor))
                        bcolor = self.correct_color(backcolor[index])
                    else:
                        bcolor = backcolor

                if textcolor is None:
                    tcolor = self.get_second_random_color(bcolor)
                else:
                    tcolor = textcolor

            index = savepath.find('.')
            filename = savepath[:index] + str(i + 1) + savepath[index:]
            img = self.draw(text, fontname=font, fontsize=font_size, save=save, savepath=filename, backcolor=bcolor, textcolor=tcolor, mode=mode)
            images.append(img)
        return images







