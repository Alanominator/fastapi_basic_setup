import random
from .letters import letters

def make_random_word():
    link_length = random.choice([*range(6, 14)])

    x = ""
    for i in range(link_length):
        x += random.choice(letters)

    return x

