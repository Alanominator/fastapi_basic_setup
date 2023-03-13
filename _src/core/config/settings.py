# """


# """


from .utils import load_env, get_env_var


load_env()



# # # email settings
EMAIL = get_env_var("EMAIL")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_PORT = 465


# google oauth2 app settings
GOOGLE_CLIENT_ID = get_env_var("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_env_var("GOOGLE_CLIENT_SECRET")


# jwt token settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30000
REFRESH_TOKEN_EXPIRE_MINUTES = 30000

# secret key (used for ecryption / decryption)
# dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64
SECRET_KEY = "SafeoMrkRus6q1A2snT2E2tjetuBXJ+WBpyUFegOnpo="
# SECRET_KEY = get_env_var("SECRET_KEY")



# TODO timezone, 

# algorithm for encryption
ALGORITHM = "HS256"