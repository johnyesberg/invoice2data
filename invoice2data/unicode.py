# -*- coding: utf-8 -*-

from unidecode import unidecode
import re
import logging
import numpy as np

UTF_MAP = {'\x80': '',  # €
           '\x81': ' ',
           '\x82': ',',
           '\x83': ',',
           '\x88': '^',
           '\x90': ' ',
           '\x91': "'",
           '\x92': "'",
           '\x93': '"',
           '\x94': '"',
           '\x96': '-',
           '\x97': '-',
           '\x98': '~',
           '\x99': '',  # ™
           '\x9a': 's',  # š
           '\x9d': ' ',
           '\xa0': ' ',
           '\xa4': '',
           '\xa6': '|',  # ¦     BROKEN BAR
           '\xaa': 'a',  # ª     FEMININE ORDINAL INDICATOR
           '\xad': '-',  # SOFT HYPHEN
           '\xb0': 'deg',  # °     DEGREE SIGN
           '\xb5': 'u',  # mu
           '\xb7': '.',  # ·     MIDDLE DOT
           '\xba': '',  # º     MASCULINE ORDINAL INDICATOR
           '\xbb': '',  # »
           '\xbc': '1/4',  # ¼     VULGAR FRACTION ONE QUARTER
           '\xbd': '1/2',  # VULGAR FRACTION ONE HALF
           # u'\u00a0': ' ',
           u'\u00be': '3/4', # ¾
           '\xbf': '?',  # ¿     INVERTED QUESTION MARK
           '\xc2': 'A',  # Â     LATIN CAPITAL LETTER A WITH CIRCUMFLEX
           '\xc3': 'A',  # Ã     LATIN CAPITAL LETTER A WITH TILDE
           u'\u0200': 'A', # with an inverted breve
           u'\u0202': 'A', # with an inverted breve
           u'\u25aa': '.', # with an inverted breve
           u'\u2010': "-", # hyphen
           u'\u2018': "'", # left single quote
           u'\u2019': "'", # right single quote
           u'\u201c': '"', # left double quotes
           u'\u201d': '"', # right double quotes
           u'\xa9': '(C)', # copyright sign
           u'\xd8': 'O',
           u'\uf0a7': '', # no idea
           u'\uf0e3': '', # no idea
           u'\uf0b7': '', # no idea
           u'\uf09f': '', # no idea
           u'\uf8e9': '', # no idea
           u'\u25aa': '',
           u'\u0373': '',
           u'\u0374': '',
           u'\u0375': '',
           u'\u0376': '',
           u'\u037b': '',
           u'\u2022' : '.',
           u'\u2212' : '-',
           u'\uf0d8' : '',
           u'\u020c' : 'O',
           u'\xb4'  : "'",
           u'\xae'  : '(R)',

           u'\ufeff': '',  # Byte order marker (?)
           '\xe2': 'a',  # â     LATIN SMALL LETTER A WITH CIRCUMFLEX
           '\xef': 'i'}  # ï      LATIN SMALL LETTER I WITH DIAERESIS


def replace_unicode_characters(str):
    a = asciify(str)
    try: 
        u = a.encode('utf-8')
    except:
        print("Couldn't unicode() %s",a)
        print type(str)
        u = a.decode('utf-8')
        assert False
    str = unidecode(u)
    a = asciify(str)
    return a


def asciify(str, replacement_map=UTF_MAP):
    """ Convert UTF-8 unicode to ASCII strings using a predefined charecter map

    Args:
        uni_string: a unicode string

    Returns:
        str or NaN: ASCII string

    """
    try:
        uni_string = unicode(str,'utf-8')
        uni_string = uni_string.encode('ascii')
        return uni_string
    except UnicodeEncodeError:
        # first, replace items from the unicode string
        for key, val in replacement_map.iteritems():
           uni_string = re.sub(key, val, uni_string)
        try:
            asc = uni_string.encode('ascii')
        except UnicodeEncodeError as e:
            logging.warn(e)
            asc = uni_string.encode('ascii', errors='ignore')
        return asc


def get_unicode_chars(unicode_string):
   """ Extract a list of the non-ASCII charecters

   Args:
       unicode_string: a unicode string

   Returns:
       list[str] or NaN: A list of all non-ASCII charecters
   """
   try:
       unicode_string.decode('ascii')
       return np.nan
   except:
       if isinstance(unicode_string, int) or isinstance(unicode_string, long):
           return np.nan
       else:
           return set([c for c in unicode_string if ord(c) > 127])

