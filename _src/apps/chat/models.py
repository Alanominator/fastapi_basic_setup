from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.hybrid import hybrid_property

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

    # histories = relationship(
    #     "RoomHistory", 
    #     back_populates="room"
    # )




class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # if user_id is null, user was deleted
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True )
    user = relationship("User", backref=backref("message", uselist=False ))

    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable = False, index = True)
    room = relationship("Room", backref=backref("message", uselist=False, cascade="all,delete" ))

    created_at = Column(DateTime(), server_default=func.now(), nullable=False)

    edited = Column(Boolean, default=False, nullable=False)

    # TODO message id deleted
    reply_to_message_id = Column("reply_to_message_id", Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True) # RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT
    reply_to_message = relationship("Message", remote_side=[id])

    _message_data = Column("message_data", JSON, nullable=False)


    @hybrid_property
    def message_data(self):
        return self._message_data
    

    @message_data.setter
    def message_data(self, data):
        if self.validate_message_data(data):
            self._message_data = data
            return
        raise Exception("data is not valid")
    

    def validate_message_data(self, data):
        # True or False
        return isinstance(data, dict)



# class RoomHistory(Base):
#     """
#     contains all room history, for example:
#     - deletions_messages
#     - changes_messages
#     """

#     __tablename__ = "rooms_histories"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable = True, index = True)
#     room = relationship("Room", backref=backref("history", uselist=False, cascade="all,delete" ))

#     _data = Column("data", JSON, nullable=False)

#     @hybrid_property
#     def data(self):
#         return self.data
        

#     @data.setter
#     def data(self, new_data):
#         if self.validate_message_data(new_data):
#             self._data = new_data
#             return
#         raise Exception("data is not valid")
        

#     def validate_data(self, new_data):
#         # True or False
#         return isinstance(new_data, dict)



# 
# (id - 28) + 1