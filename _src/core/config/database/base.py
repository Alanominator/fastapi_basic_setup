"""
File contains "Base" object.

This variable should be imported from another files with models, which inherits "Base class"

And then into this file we should import models like "from .models import *"

"""


from sqlalchemy.orm import declarative_base


Base = declarative_base()


# -> # register your models here
# from core.models import *
from apps.auth.models import *
from apps.chat.models import *

