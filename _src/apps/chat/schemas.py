from typing import List, Literal, Optional
from pydantic import BaseModel







class RoomResponse(BaseModel):
    id: str
    name: str
    link: str
    description: Optional[str or None]
    # created_at: any
    # members: List



class TextMessageData(BaseModel):
    message_type: Literal["text_message"]
    text: str