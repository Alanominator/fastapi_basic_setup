from datetime import date, time, datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel
# from datetime import datetime





class RoomResponse(BaseModel):
    id: str
    name: str
    link: str
    description: Optional[str or None]
    created_at: datetime
    # members: List

    # class Config:
    #     orm_mode = True



class MessageResponse(BaseModel):
    id: str
    user_id: int
    # room_id: int
    edited: bool
    date: date
    time: time
    # reply_to_message: Any
    message_data: dict

    # reply_to_message_id | message_data

class TextMessageData(BaseModel):
    message_type: Literal["text_message"]
    text: str