from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List


# class EmailSchema(BaseModel):
#     email: List[EmailStr]


# email_connection_config = ConnectionConfig(
#     MAIL_USERNAME ="username",
#     MAIL_PASSWORD = "**********",
#     MAIL_FROM = "test@email.com",
#     MAIL_PORT = 465,
#     MAIL_SERVER = "mail server",
#     MAIL_STARTTLS = False,
#     MAIL_SSL_TLS = True,
#     USE_CREDENTIALS = True,
#     VALIDATE_CERTS = True
# )


GOOGLE_CLIENT_ID = "598977301108-80aknbj43qfhrbm9h25o33q8sk5m5rpj.apps.googleusercontent.com"

GOOGLE_CLIENT_SECRET = "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"





ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 30

# dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64
SECRET_KEY = "SafeoMrkRus6q1A2snT2E2tjetuBXJ+WBpyUFegOnpo="


# TODO timezone, 



ALGORITHM = "HS256"