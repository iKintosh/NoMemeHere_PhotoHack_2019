import pymorphy2
import numpy as np
import re

def is_time_format(s):
    time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
    return bool(time_re.match(s))

def get_sublists(word_list, indices, add=0):
    sublists = [] #[word_list[:indices[0] + 1]]
    for i in range(len(indices) - 1):
        sublists.append(word_list[indices[i]+add:indices[i + 1]+add])
    sublists.append(word_list[indices[-1]+add:])
    return sublists

def check_list_structure(msg, morph_an):
    POS_list = [None] * len(msg)
    for i, phrase in enumerate(msg):
        inner_list = [None] * len(phrase)
        for j, word in enumerate(phrase):
            inner_list[j] = morph_an.parse(word)[0].tag.POS
        POS_list[i] = inner_list
    prob = [probability(POS_list[i], POS_list[:i]+POS_list[i+1:]) for i in range(len(POS_list))]
    return(np.mean(prob))


def probability(lst, POS_except_lst):
    len_lst = len(lst)
    cnt = 0

    if lst in POS_except_lst:
        return 1.0

    for word in lst:
        word_cnt = 0
        for check_lst in POS_except_lst:
            if word in check_lst:
                word_cnt += 1
        cnt += word_cnt / len(POS_except_lst)

    return cnt / len_lst

def isListComma(word_list,morph_an):

    if 'и' in word_list:
        for _ in range(word_list.count('и')):
            word_list[word_list.index('и')] = ','

    if word_list.count(',')>1:
        indices = [i for i, x in enumerate(word_list) if x == ","]
        indices.insert(0,-1)
        if check_list_structure(get_sublists(word_list, indices, add=1), morph_an) >= 0.7:
            return (True, get_sublists(word_list, indices, add=1))
        else:
            return (False, None)
    else:
        return (False, None)

def isListNoun(word_list,morph_an):
    morph_list = []
    for word in word_list:
        morph_list.append(morph_an.parse(word)[0])
    cases = []
    indices = []
    for i, morph in enumerate(morph_list):
        if 'NOUN' in morph.tag:
            case = morph.tag.case
            cases.append(case)
            indices.append(i)
        if 'VERB' in morph.tag:
            return (False, None)
    if len(cases) > 2:
        if indices[0] != 0:
            indices.insert(0, 0)
        return (True, get_sublists(word_list, indices))
    return (False, None)

def isListInfn(word_list, morph_an):
    morph_list = []
    for word in word_list:
        morph_list.append(morph_an.parse(word)[0])
    morphs = []
    indices = []
    for i, morph in enumerate(morph_list):
        if 'INFN' in morph.tag:
            indices.append(i)
    if len(morphs) > 2:
        if indices[0] != 0:
            indices.insert(0, 0)
        return (True, get_sublists(word_list, indices))
    return (False, None)


def isListVerb(word_list, morph_an):
    morph_list = []
    for word in word_list:
        morph_list.append(morph_an.parse(word)[0])
    morphs = []
    indices = []
    for i, morph in enumerate(morph_list):
        if 'VERB' in morph.tag:
            morphs.append(morph)
            indices.append(i)
    if len(morphs) > 2:
        for morph in morphs[1:]:
            if morph.tag.tense != morphs[0].tag.tense or morph.tag.mood != morphs[0].tag.mood:
                return (False, None)
        if indices[0] != 0:
            indices.insert(0, 0)
        return (True, get_sublists(word_list, indices))
    return (False, None)

def isListNum(word_list, morph_an):
    morph_list = []
    for word in word_list:
        morph_list.append(morph_an.parse(word)[0])
    nums = []
    indices = []
    for i, morph in enumerate(morph_list):
        if not is_time_format(morph.word):
            continue
        if 'NUMB' in morph.tag and 'real' in morph.tag:
            word = morph.word
            if word.isdigit():
                nums.append(int(word))
            else:
                nums.append(int(word[:-1]))
            indices.append(i)
    if len(nums)>2:
        if abs(nums[1]-nums[0]) == 1 and abs(nums[2]-nums[1]) == 1:
            if indices[0] != 0:
                indices.insert(0,0)
            return (True, get_sublists(word_list, indices))
    return (False, None)

def getWords(text):
    words = text.split(' ')
    return words

def parsePunctuation(word_list, punct_list = ['...', '..','.', '?!', '!', '?', ',', ':', ';'], exclude_list=[]):
    new_list = []
    #exclude_list = ['..']
    for word in word_list:
        ch = False
        for punct in punct_list:
            w_s = word.split(punct)
            if len(w_s)>1:
                if w_s[1]=='':
                    if punct not in exclude_list and not w_s[0].isdigit():
                        new_list.append(w_s[0])
                        new_list.append(punct)
                        ch = True
                    break
                else:
                    new_list.append(word)
        if not ch:
            new_list.append(word)
    return new_list

def isList(text):
    word_list = getWords(text)
    parsed_word_list = parsePunctuation(word_list)
    morph_an = pymorphy2.MorphAnalyzer()
    for islist in [isListNum, isListComma, isListInfn, isListVerb, isListNoun]:
        res, sublists = islist(parsed_word_list, morph_an)
        if res:
            return sublists
    else:
        return False


text2 = "купи молока, приготовь завтрак, выиграй хакатон!"
text3 = "1. молоко 2. завтрак 3. хакатон?!"
text4 = "секс наркотики рок-н-ролл"
text5 = 'Кароче есть места в рабочей зоне, но там музло играет, сели там же где и вчера, тут тихо и еда близко)'
text6 = 'я через 10 минут пришлю код. себя пришлю через час('
text7 = 'античный город, осень, серое небо, каменная дорога, деревья, карета с лошадьми, воины на лошадях '
text8 = 'Купи три пачки чая, кг сахара и конфеты'


# if __name__ == '__main__':
#     print(isList(text2))
#     print(isList(text3))
#     print(isList(text4))
#     print(isList(text5))
#     print(isList(text6))
#     print(isList(text8))
