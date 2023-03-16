from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref


from core.config.database.base import Base
from . import utils
from core.utils import hash_string, verify_hashed_string



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(40), unique=True, index=True, nullable=False)
    # todo username
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    _password_hash = Column("password", String(), nullable=False)


    # todo
    auth_sessions = relationship(
        "AuthSession",
        back_populates="user"
    )

    rooms = relationship(
        "Room",
        secondary="room_members",
        back_populates="members"
    )


    # todo admin in rooms || rooms under administration
    admin_in = relationship(
        "Room",
        secondary="room_admins",
        back_populates="admins"
    )


    @hybrid_property
    def password(self):
        return self._password_hash
    
    @password.setter
    def password(self, plain_password):
        self._password_hash = hash_string(plain_password)


    def verify_password(self, plain_password: str) -> bool:
        """
            Returns True, if user's password is <plain_password>. Else returns False
        """
        return verify_hashed_string(plain_password, self._password_hash)



class ActivationToken(Base):
    __tablename__ = "activation_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    token = Column(String(32), nullable=False, default = lambda : utils.gen_string(32) )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True )
    user = relationship("User", backref=backref("activation_token", uselist=False, cascade="all,delete" ))




class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable = False, index = True)

    user = relationship("User", backref=backref("auth_session", uselist=False, cascade="all,delete" ))

    _access_jwt_token_hash = Column("access_jwt_token", String(), nullable = False)

    # type of session

    @hybrid_property
    def access_jwt_token(self):
        return self._access_jwt_token_hash
    

    @access_jwt_token.setter
    def access_jwt_token(self, plain_access_jwt_token):
        self._access_jwt_token_hash = hash_string(plain_access_jwt_token)
    

    # TODO -> method
    def verify_access_jwt_token(self, plain_access_jwt_token: str) -> bool:
        return verify_hashed_string(plain_access_jwt_token, self._access_jwt_token_hash)




# class Captcha(models.Model):
#     value = models.CharField("value", max_length=500)
#     date = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return self.value