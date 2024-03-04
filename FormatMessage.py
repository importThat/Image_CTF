import re

"""
Program to format a message into all caps and only including the letters A-Z,.!
"""

def read_message(fn):
    text = ''

    with open(fn, "r", encoding='utf-8') as f:
        for line in f:
            text += line

    return text


not_valid = re.compile(r"[^A-Z ,.!]")
text = read_message("message2.txt")
text = text.upper()
text = re.sub(r"\n", " ", text)
text = re.sub(not_valid, "", text)

with open("longer_message.txt", "w") as f:
    f.writelines(text)


