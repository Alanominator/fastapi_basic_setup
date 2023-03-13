from core.config.database.database import SessionLocal;
from apps.auth.models import User;
from apps.chat.models import Room, Message;

db = SessionLocal()

u = db.query(User).filter(User.id == 3).first()

# r = Room(
#     link = "qqq",
#     name = "Group name"
# )



# r = db.query(Room).filter(Room.link == "qqq").first()

# r.members.append(u)
# r.admins.append(u)

# db.add(r)
# db.commit()
# db.refresh(r)
# db.refresh(u)

# print(u.admin_in)

# m = Message(
#     user_id = u.id,
#     room_id = r.id,
#     text = "hello world"
# )

# db.add(m)

# db.commit()
# db.refresh(m)
# db.refresh(r)

print("\n\n\n\n\n")

rooms_list = u.rooms



from pydantic import BaseModel



class RoomResponse(BaseModel):
    name: str
    link: str


    # schemas.UserResponse.parse_obj(db_user.__dict__).dict()



# print("\n\n\n\n")
# print(
#     RoomResponse.serialize()
# )
