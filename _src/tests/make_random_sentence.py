import random
from .lorem_words import lorem_words

def make_sentence(length=None):
    if length == None:
        length = random.choice([*range(5, 10)])
    
    x = ""
    for i in range(length):
        x += random.choice(lorem_words)
        x += " "
    
    return x


if __name__ == "__main__":
    print(
        make_sentence(2)
    )