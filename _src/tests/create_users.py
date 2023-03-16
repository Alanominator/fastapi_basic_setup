from .make_random_link import create_random_link
from core.config.database.database import SessionLocal;
from apps.auth.models import User;
from .make_random_sentence import make_sentence
import random

db = SessionLocal()



def main():
    for i in range(100):
        u = User(
            email = create_random_link(),
            is_active = True,
            password = make_sentence(2)
        )
        db.add(u)

    db.commit()


