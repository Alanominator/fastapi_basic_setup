import random
from .lorem_words import lorem_words

def make_random_sentence(
    length=random.choice([1, 4, 30, 100]) 
):
    # length=random.choice([*range(1, 20)]) 
    x = ""
    for i in range(length):
        x += random.choice(lorem_words)[:5]
        x += " "
    
    return x

