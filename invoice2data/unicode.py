def replace_unicode_characters(str):
    a = str.decode("utf-8").replace(u"\u2212", "-").encode("utf-8")
    return a
