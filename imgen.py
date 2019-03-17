from PIL import Image
from genetic import GeneticAlgorithm
import numpy as np
from copy import deepcopy

class ImageGenerator():
    def __init__(self, path_to_img):
        self.image = Image.open(path_to_img)
        self.images = []
        self.sizes = []
        self.space = 10
        self.func = None

    def count(self):
        return len(self.images)

    def imgsize(self):
        return self.image.size

    def imgwidth(self):
        return self.image.size[0]

    def imgheight(self):
        return self.image.size[1]

    def init_minimizator(self, images, rect=None):
        self.images = images
        self.sizes = [im.size for im in images]
        self.rect = rect
        max_vals = [self.imgwidth() - s[0] for s in self.sizes]
        max_vals.extend([self.imgheight() - s[1] for s in self.sizes])

        ga = GeneticAlgorithm()
        ga.population = 150
        ga.n_iters = 1000
        ga.mutation_prob = 0.4
        ga.dim = 2 * self.count()
        ga.mutation_factor = min(self.imgwidth(), self.imgheight()) / 2
        ga.set_minvals(0)
        ga.set_maxvals(max_vals)
        return ga

    def avoid_rect(self, rect, images):
        self.func = self.fitness_avoid_rect
        ga = self.init_minimizator(images, rect=rect)
        _, minx = ga.minimize(self.fitness)
        return minx

    def create_list(self, images):
        self.func = self.fitness_create_list
        ga = self.init_minimizator(images)
        _, minx = ga.minimize(self.fitness)
        return minx

    def create_celllist(self, images, x_offset=50, y_offset=100):
        def check(y_offset):
            h = sum([s[1] for s in self.sizes]) + self.space * (self.count() - 1) + y_offset
            return h <= self.imgheight()

        self.images = images
        self.sizes = [im.size for im in images]
        maxheight = np.max([s[1] for s in self.sizes])
        if check(y_offset):
            maxwidth = self.imgheight()
        else:
            maxwidth = np.max([s[0] for s in self.sizes])
        n_cols = int(np.floor(self.imgwidth() / maxwidth))
        n_rows = int(np.floor(self.count() / n_cols))
        height_all = n_rows * maxheight + (self.count() - 1) * self.space
        if height_all + y_offset <= self.imgheight():
            x, y = [], []
            for i in range(self.count()):
                col = i % n_cols
                row = i // n_cols
                x.append(x_offset + col * (maxwidth + self.space))
                y.append(y_offset + row * (maxheight + self.space))
            x.extend(y)
            return np.array(x)
        return None

    def fitness(self, x):
        if len(x.shape) == 1:
            return self.func(x)
        result = np.zeros(x.shape[0])
        for counter, row in enumerate(x):
            result[counter] = self.func(row)
        return result

    def trans_paste(self, fg_img, bg_img, alpha=1.0, box=(0, 0)):
        fg_img_trans = Image.new("RGBA", fg_img.size)
        fg_img_trans = Image.blend(fg_img_trans, fg_img, alpha)
        bg_img.paste(fg_img_trans, box, fg_img_trans)
        return bg_img

    def fitness_avoid_rect(self, v):
        f = 0
        x = v[np.arange(0, self.count())]
        y = v[np.arange(self.count(), 2 * self.count())]
        # Расчет пересечений
        inters = 0
        for i in range(self.count() - 1):
            for j in range(i + 1, self.count()):
                inters += self.intersection((x[i] - self.space, y[i] - self.space, self.sizes[i][0] + 2 * self.space, self.sizes[i][1] + 2 * self.space),
                                            (x[j] - self.space, y[j] - self.space, self.sizes[j][0] + 2 * self.space, self.sizes[j][1] + 2 * self.space))
        f += np.sqrt(inters)
        # Расчет порядка
        order = 0
        coeff = 0.66
        for i in range(self.count()):
            for j in range(i + 1, self.count()):
                if y[i] + coeff * self.sizes[i][1] > y[j]:
                    order += y[i] + coeff * self.sizes[i][1] - y[j]
                if x[i] > x[j]:
                    order += 1
        f += 0.5 * order
        # Расчет пересечений с областью
        inters = 0
        for i in range(self.count()):
            inters += self.intersection((x[i] - self.space, y[i] - self.space, self.sizes[i][0] + 2 * self.space, self.sizes[i][1] + 2 * self.space), self.rect)
        f += np.sqrt(inters)
        return f

    def fitness_create_list(self, v):
        f = 0
        x = v[np.arange(0, self.count())]
        y = v[np.arange(self.count(), 2 * self.count())]
        # Расчет пересечений
        inters = 0
        for i in range(self.count() - 1):
            for j in range(i + 1, self.count()):
                inters += self.intersection((x[i] - self.space, y[i] - self.space, self.sizes[i][0] + 2 * self.space, self.sizes[i][1] + 2 * self.space),
                                            (x[j] - self.space, y[j] - self.space, self.sizes[j][0] + 2 * self.space, self.sizes[j][1] + 2 * self.space))
        f += np.sqrt(inters)
        # Расчет сетчатости
        delta = 10
        gridness = 100
        for i in range(self.count() - 1):
            for j in range(i + 1, self.count()):
                if (x[j] >= x[i] - delta) and (x[j] <= x[i] + delta):
                    gridness -= 10
                if (y[j] >= y[i] - delta) and (y[j] <= y[i] + delta):
                    gridness -= 3
        f += gridness
        # Расчет общей занимаемой площади
        delta = 20
        x_left = np.min(x)
        x_right = np.max([x[i] + self.sizes[i][0] for i in range(self.count())])
        y_top = np.min(y)
        y_bottom = np.max([y[i] + self.sizes[i][1] for i in range(self.count())])
        f += np.sqrt(abs((self.imgwidth() - delta) * (self.imgheight() - delta) - (x_right - x_left) * (y_bottom - y_top)))
        return f

    def intersection(self, rect1, rect2):
        dx = min(rect1[0] + rect1[2], rect2[0] + rect2[2]) - max(rect1[0], rect2[0])
        dy = min(rect1[1] + rect1[3], rect2[1] + rect2[3]) - max(rect1[1], rect2[1])
        if (dx >= 0) and (dy >= 0):
            return dx * dy
        return 0

    def plot(self, v, save=False, savepath='image.png'):
        x = v[np.arange(0, self.count())]
        y = v[np.arange(self.count(), 2 * self.count())]
        img = deepcopy(self.image)
        for i in range(self.count()):
            img = self.trans_paste(self.images[i], img, box=(x[i], y[i]))
        if save:
            img.save(savepath)
        img.show()

    def save(self, v, savepath='image.png'):
        x = v[np.arange(0, self.count())]
        y = v[np.arange(self.count(), 2 * self.count())]
        img = deepcopy(self.image)
        for i in range(self.count()):
            img = self.trans_paste(self.images[i], img, box=(x[i], y[i]))
        img.save(savepath)





