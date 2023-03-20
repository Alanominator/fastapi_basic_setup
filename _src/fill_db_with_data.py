
import json
from apps.chat import models as chat_models
from apps.auth import models as auth_models
from core.config.database.database import SessionLocal;
from sqlalchemy.orm import sessionmaker
from tests.make_random_word import make_random_word
from tests.make_random_sentence import make_random_sentence
import random

db: sessionmaker = SessionLocal()


def main():
    # test users
    test_users = [
        {
            "email": "test1@gmail.com",
            "password": "helloworld"
        },
        {
            "email": "amurik@gmail.com",
            "password": "amurik2029"
        }
    ]

    used_emails = [x[0] for x in list(db.query(auth_models.User.email))]
    try:
        for i in test_users:
            if i["email"] in used_emails:
                continue

            u = auth_models.User(
                email = i["email"],
                is_active = True,
                password = i["password"]
            )
            db.add(u)
        db.commit()
    except Exception as e:
        print("[-] ", e)


    # users
    users = [0] * 5
    for i in range(len(users)):
        u = auth_models.User(
            email = make_random_word(),
            is_active = True,
            password = make_random_sentence(2)
        )
        users[i] = u
        db.add(u)
    db.commit()
    

    # rooms
    rooms = [0] * 10
    for i in range(len(rooms)):
        r = chat_models.Room(
            link = make_random_word(),
            name = make_random_sentence(random.choice([1,1,1,2]))
        )
        rooms[i] = r
        db.add(r)
    db.commit()
    

    users_ids = [x[0] for x in list(db.query(auth_models.User.id))]
    rooms_ids = [x[0] for x in list(db.query(chat_models.Room.id))]


    # add random users to random rooms
    used = [[x.user_id, x.room_id] for x in list(db.query(chat_models.RoomMembers))]

    for i in range(100):
        x = [random.choice(users_ids), random.choice(rooms_ids)]

        if x in used:
            continue
        else:
            used.append(x)

        ur = chat_models.RoomMembers(
            user_id = x[0],
            room_id = x[1]
        )
        db.add(ur)
    db.commit()


    # create random messages
    used = [[x.user_id, x.room_id] for x in list(db.query(chat_models.RoomMembers))]

    for i in range(2000):
        x = random.choice(used)
        print(x)

        m = chat_models.Message(
            user_id = x[0],
            room_id = x[1],
            message_data = {
                "message_type": "text_message",
                "test": make_random_sentence()
            }
        )
        db.add(m) 
    db.commit()



if __name__ == "__main__":
    """"""
    main()
    
    print("\n[+] Database filled")

    # db.query(models.Room).join(models.RoomMembers).where(models.Room.id == models.RoomMembers.room_id).where(models.RoomMembers.user_id == user.id)

    """

    SELECT messages.*, rooms.link AS room_link 
    FROM messages 
    JOIN rooms ON messages.room_id = rooms.id
    WHERE messages.room_id = 197 
    AND messages.id < 49000
    ORDER BY messages.id DESC 
    LIMIT 15;
    
    """
    print(
        json.dumps(
            [x.__dict__ for x in
                list(
                    db.query(chat_models.Message)
                        .join(chat_models.Room)
                        .where(chat_models.Message.room_id == chat_models.Room.id)
                        .where(chat_models.Message.room_id == 197)
                        .order_by(chat_models.Message.id.desc())
                        .limit(15)
                )
            ],
            indent=4,
            default=str
        )
    )
    
