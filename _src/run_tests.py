
from apps.chat import models, schemas
from core.config.database.database import SessionLocal;

from sqlalchemy.orm import sessionmaker

db: sessionmaker = SessionLocal()


print("\n\n\n\n")

# print(
#     db.query().with_entities(RoomMembers.room_id).filter(RoomMembers.user_id == 10)
# )

print(
    # select * from rooms join room_members on id = room_id;
)

#  select * from rooms join room_members on id = room_id;


# select * from rooms join room_members on id = room_id where user_id = 4;


"""

SELECT * FROM rooms JOIN room_members ON rooms.id = room_members.room_id WHERE rooms.id = room_members.room_id AND room_members.user_id = 10;

"""
    
# print(

# [
#     schemas.RoomResponse.parse_obj(room.__dict__).dict()
#         for room in 
#             db.query(models.Room).join(models.RoomMembers).where(models.Room.id == models.RoomMembers.room_id).where(models.RoomMembers.user_id == 10)
# ]

# )

# print(
#     dir(
#         db.query()
#     )
# )


# if __name__ == "__main__":
#     # create_rooms.main()
#     create_users.main()
