import random
from .letters import letters

def create_random_link():
    link_length = random.choice([*range(6, 14)])

    x = ""
    for i in range(link_length):
        x += random.choice(letters)

    return x


print(create_random_link())