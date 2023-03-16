from core.config.database.database import SessionLocal;
from apps.auth.models import User;
from apps.chat.models import Room, Message;

db = SessionLocal()

u = db.query(User).filter(User.id == 4).first()

# r = Room(
#     link = "www",
#     name = "Group name"
# )



r = db.query(Room).filter(Room.id == 3).first()

# r.members.append(u)
# # r.admins.append(u)

# db.add(r)
# db.commit()
# db.refresh(r)
# db.refresh(u)

# # print(u.admin_in)



# # db.add(m)

# # db.commit()
# # db.refresh(m)
# # db.refresh(r)

# print("\n\n\n\n\n")

print(u.rooms)


# from pydantic import BaseModel



# class RoomResponse(BaseModel):
#     name: str
#     link: str


#     # schemas.UserResponse.parse_obj(db_user.__dict__).dict()



# # print("\n\n\n\n")
# # print(
# #     RoomResponse.serialize()
# # )


# for i in range(10000):
#     m = Message(
#         user_id = u.id,
#         room_id = r.id,
#         # reply_to_message_id = 61,
#         message_data = {"message_type": "text_message", "text": "hello"}
#     )

#     db.add(m)


# r.messages



# m = db.query(Message).filter(Message.id == 62).first()


# db.commit()

# m.message_data = {"message_type": "text_message", "text": "edited"}
# m.edited = True

# db.commit()


# print("\n\n\n\n")

# print(u.auth_sessions)

# print(m.reply_to_message)

# db.commit()
