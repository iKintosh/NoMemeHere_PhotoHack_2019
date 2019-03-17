import pymorphy2
from dateutil.parser import parse
import datetime
import stop_words as sw
import re


def time_message_detect(message='Встреча 29.03.19 в 14:00'):
    morph = pymorphy2.MorphAnalyzer()
    message = message.lower()
    message = message.split()
    flags = [False] * len(message)

    for i, word in enumerate(message):
        lex = morph.parse(word)[0]

        if 'UNKN' in lex.tag:
            flags[i] = is_this_date(word) or is_this_time(word)

        elif 'NUMR' in lex.tag or 'NUMB' in lex.tag:
            flags[i] = near_detector(message, i, sw.prep_words) or near_detector(message, i, sw.time_words)

        elif lex.normal_form in sw.day_words or lex.normal_form in sw.other_words or lex.normal_form in sw.time_words:
            flags[i] = True
    return [message, flags]


def is_this_time(num_str):
    num_str = delim(num_str)
    if len(num_str) == 2:
        num_str = ':'.join(num_str)
        try:
            _ = parse(num_str)
            return True
        except ValueError:
            pass
    return False


def is_this_date(num_str):
    num_str = delim(num_str)
    if len(num_str) == 2:
        num_str.append(str(datetime.date.today().year))
        num_str = '/'.join(num_str)
        try:
            _ = parse(num_str)
            return True
        except ValueError:
            pass
    if len(num_str) == 3:
        num_str = '/'.join(num_str)
        try:
            _ = parse(num_str)
            return True
        except ValueError:
            pass
    return False


def near_detector(message, indx, list_words):
    morph = pymorphy2.MorphAnalyzer()
    if len(message) == 1:
        return True
    elif indx == 0:
        nxt = morph.parse(message[indx + 1])[0].normal_form
        prev = None
    elif indx == len(message) - 1:
        prev = morph.parse(message[indx - 1])[0].normal_form
        nxt = None
    else:
        nxt = morph.parse(message[indx + 1])[0].normal_form
        prev = morph.parse(message[indx - 1])[0].normal_form

    return prev in list_words or nxt in list_words


def delim(num_str):
    num_str = re.sub("[^0-9]", " ", num_str).split()
    return num_str


if __name__ == '__main__':
    print(time_message_detect('Купи три пачки чая, кг сахара и конфеты'))
