import random
from .lorem_words import lorem_words

def make_random_sentence(length=None):
    if length == None:
        length = random.choice([*range(5, 7)])
    
    x = ""
    for i in range(length):
        x += random.choice(lorem_words)[:5]
        x += " "
    
    return x

