import email
from typing import List
from pydantic import BaseModel



# class UserInfoByWS(BaseModel):
#     email: str
#     is_admin: str




class RoomResponse(BaseModel):
    name: str
    link: str
    # members: List

# "room_data": {
#             //         "name": "Hello world",
#             //         "link": "qqqq",
#             //         "photos": [],
#             //         "members": [],
#             //     },