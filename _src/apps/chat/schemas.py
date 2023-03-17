from typing import List, Literal, Optional
from pydantic import BaseModel
# from datetime import datetime





class RoomResponse(BaseModel):
    id: str
    name: str
    link: str
    descriptio1n: Optional[str or None]
    # created_at: datetime
    # members: List


class MessageResponse(BaseModel):
    id: str
    user_id: int
    room_id: int
    edited: bool
    # created_at: ""
    # created_at: datetime
    # reply_to_message
    message_data: dict

    #created_at         | reply_to_message_id |                   message_data

class TextMessageData(BaseModel):
    message_type: Literal["text_message"]
    text: str