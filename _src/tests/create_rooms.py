from .make_random_link import create_random_link
from core.config.database.database import SessionLocal;
from apps.chat.models import Room;
from .make_random_sentence import make_sentence
import random

db = SessionLocal()



def main():
    for i in range(500):
        r = Room(
            link = create_random_link(),
            name = make_sentence(random.choice([1,1,1,2]))
        )
        print(r.name)
        db.add(r)

    db.commit()


