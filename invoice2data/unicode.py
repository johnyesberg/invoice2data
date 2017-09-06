# -*- coding: utf-8 -*-

from unidecode import unidecode
import re
import logging
import numpy as np

UTF_MAP = {'\x80': '',  # €
           '\x81': ' ',
           '\x82': ',',
           '\x88': '^',
           '\x90': ' ',
           '\x91': "'",
           '\x92': "'",
           '\x93': '"',
           '\x94': '"',
           '\x96': '-',
           '\x97': '-',
           '\x99': '',  # ™
           '\x9a': 's',  # š
           '\x9d': ' ',
           '\xa0': ' ',
           '\xa6': '|',  # ¦     BROKEN BAR
           '\xaa': 'a',  # ª     FEMININE ORDINAL INDICATOR
           '\xad': '-',  # SOFT HYPHEN
           '\xb0': 'deg',  # °     DEGREE SIGN
           '\xb7': '.',  # ·     MIDDLE DOT
           '\xba': '',  # º     MASCULINE ORDINAL INDICATOR
           '\xbb': '',
           '\xbc': '1/4',  # ¼     VULGAR FRACTION ONE QUARTER
           '\xbd': '1/2',  # VULGAR FRACTION ONE HALF
           '\xbf': '?',  # ¿     INVERTED QUESTION MARK
           '\xc2': 'A',  # Â     LATIN CAPITAL LETTER A WITH CIRCUMFLEX
           '\xc3': 'A',  # Ã     LATIN CAPITAL LETTER A WITH TILDE
           '\xe2': 'a',  # â     LATIN SMALL LETTER A WITH CIRCUMFLEX
           '\xef': 'i'}  # ï      LATIN SMALL LETTER I WITH DIAERESIS


def replace_unicode_characters(str):
    u = unicode(str,'utf-8')
    str = unidecode(u)
    a = asciify(str)
    return a


def asciify(uni_string, replacement_map=UTF_MAP):
   """ Convert UTF-8 unicode to ASCII strings using a predefined charecter map

   Args:
       uni_string: a unicode string

   Returns:
       str or NaN: ASCII string

   """
   try:
       uni_string = uni_string.decode('ascii')
       return uni_string
   except UnicodeDecodeError:
       for key, val in replacement_map.iteritems():
           uni_string = re.sub(key, val, uni_string)

       try:
           uni_string = uni_string.decode('ascii')
           return uni_string
       except UnicodeDecodeError:
           logging.warning("Could not asciify %s " % uni_string)
           c = get_unicode_chars(uni_string)
           logging.warning(c)
           assert False
           return np.nan


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

