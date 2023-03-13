from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

from core.config.database.base import Base



class RoomMembers(Base):
    __tablename__ = "room_members"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)

class RoomAdmins(Base):
    __tablename__ = "room_admins"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)




class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    link = Column(String(20), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)

    description = Column(Text()) # 100
    # TODO photos

    admins = relationship(
        "User",
        secondary="room_admins",
        back_populates="admin_in"
    )

    members = relationship(
        "User",
        secondary="room_members",
        back_populates="rooms"
    )

    messages = relationship(
        "Message", 
        back_populates="room"
    )




class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True )
    user = relationship("User", backref=backref("message", uselist=False ))

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable = False, index = True)
    room = relationship("Room", backref=backref("message", uselist=False ))

    text = Column(Text(), nullable=False)

    edited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    
    # todo reply to message, one to one relation
    # reply_to_message_id = Column("Message", ForeignKey("messages.id"), nullable=True)
    # reply_to_message = relationship("Message", )



