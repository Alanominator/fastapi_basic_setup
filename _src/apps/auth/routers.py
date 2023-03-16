import fastapi
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.config.database.utils import get_db

from . import exceptions
from . import crud
from . import schemas
from . import utils
from . import tasks
from . import models

import urllib.parse

from core.config import settings

import requests

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader

from fastapi.responses import StreamingResponse

from fast_captcha import img_captcha


from retry import retry
import requests

from fastapi.responses import HTMLResponse

from core.utils import encrypt_string, decrypt_string
from jose import jwt



auth_router = fastapi.APIRouter(
    prefix="/users"
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):

    user = utils.get_user_by_access_token(
        access_token = token
    )

    return user



# TODO
"""
change some response status codes

fix schemes
"""




# # TODO
# @auth_router.get('/captcha', summary='captcha', name='captcha')
# def get_captcha():
#     img, text = img_captcha()

#     # send hash of encrypted text
#     # it is not safe

#     return StreamingResponse(content=img, media_type='image/jpeg')


# @api_view(['POST'])
# def recaptcha(request):
#     captcha_value = request.data['captcha_value']

#     if captcha_value:
#         r = requests.post(
#             'https://www.google.com/recaptcha/api/siteverify',
#             data={
#                 'secret': settings.CAPTCHA_SECRET_KEY,
#                 'response': captcha_value,
#             }
#         )

#         if r.json()["success"]:

#             c = Captcha.objects.create(value = captcha_value)
#             c.save()

#             delete_recaptcha.apply_async(countdown = 60 * 2, kwargs = {"id": c.id})

#             return Response(data={'captcha': True}, status=status.HTTP_200_OK)
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#     return Response(status=status.HTTP_403_FORBIDDEN)






@auth_router.post("/register")
async def register_user(*,
    user: schemas.UserCreate = fastapi.Body(),
    db: Session = Depends(get_db)
):

    errors_to_send = []


    # todo recaptcha
        #     try:
        #     if not captcha_value:
        #         raise

        #     c = Captcha.objects.filter(value = captcha_value)[0]

        #     x1 = int(timezone.now().strftime("%s"))
        #     x2 = int(c.date.strftime("%s"))
        #     delta_in_seconds = (x1 - x2)

        #     seconds = round(60 - delta_in_seconds, 1)

        #     if seconds > 60 * 2:
        #         c.delete()
        #         return Response(data={"messages": [f"Captcha has expired", ]}, status=status.HTTP_400_BAD_REQUEST)

        #     c.delete()
        # except:
        #     return Response(data={"messages": [f"Captcha is wrong", ]}, status=status.HTTP_400_BAD_REQUEST)



    # check if user with given email exists, if yes, raise 400
    if ( crud.get_user_by_email(db, email = user.email) ):
        errors_to_send.append("User with this email already exists")


    # validate email
    if not utils.isEmailValid(user.email):
        errors_to_send.push("Email is not valid")

    # validate password
    if not utils.isPasswordValid(user.password):
        errors_to_send.push("Password is invalid")

    # if password_confirmation not equals to password, raise error
    if not user.password == user.password_confirmation:
        errors_to_send.push("Password confirmation must be equal to password")

    if len(errors_to_send) > 0:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
            detail = {
                "errors": errors_to_send
            }
        )


    # Everything is ok, register ->>

    # run celery tasks
    tasks.register_task.delay(
        email = user.email,
        password = user.password
    )


    return JSONResponse(
        status_code = status.HTTP_201_CREATED,
        content = {
            "message":"User created. Activation link was sent to your email"
        }
    )





# TODO
# @auth_router.get("/resend_actition_password")
# async def resend_actition_password(*,
#     db: Session = Depends(get_db)
# ):
#     pass





@auth_router.get("/activate")
async def activate_user(*,
    token: str = fastapi.Query(min_length=5),
    db: Session = Depends(get_db)
):

    db_token = crud.get_activation_token_by_token(db, 
        token = token
    )

    # TODO return html template
    if not db_token:
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content={
            "message":"Token was not found"
        })

    # todo check token time
    # DELETE_INACTIVE_USER_TIMEOUT_MIN


    db_token.user.is_active = True
    db.delete(db_token)
    db.commit()


    # TODO redirect to frontend
    return {
        "hello": f"Your account has been activated"
    }




@auth_router.post("/login")
async def login(
    user: schemas.UserLogin = fastapi.Body(),
    db: Session = Depends(get_db)
):

    email = user.email
    password = user.password


    db_user = crud.get_user_by_email(db, email)

    if not db_user or not db_user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not db_user.is_active:
        raise exceptions.inactive_user


    # TODO count sessions

    user_id = db_user.id

    jwt_tokens = utils.create_auth_session_and_get_jwt_tokens(user_id)

    user = schemas.UserResponse.parse_obj(db_user.__dict__).dict()


    return {
        "user": user,
        "jwt_tokens": jwt_tokens
    }









@auth_router.get("/google_auth_consent", response_class=RedirectResponse)
def google_auth_consent():
    """
    function redirects to google auth consent
    """

    # https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?client_id=598977301108-80aknbj43qfhrbm9h25o33q8sk5m5rpj.apps.googleusercontent.com&response_type=token&scope=profile&redirect_uri=http%3A%2F%2Flocalhost%3A8000&service=lso&o2v=2&flowName=GeneralOAuthFlow

    url_base = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?"

    url_params = {
        'client_id': settings.GOOGLE_CLIENT_ID,

        # frontend url
        'redirect_uri': 'http://localhost:8000/users/google_auth_page',
        
        'response_type': 'token',
        
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        # 'include_granted_scopes': 'true',
        'state': 'pass-through value'
    }


    url_for_redirect = url_base + urllib.parse.urlencode(url_params)


    return RedirectResponse(url_for_redirect)





#@auth_router.get("/google_auth_page") # response_class=RedirectResponse
#def google_auth_page():
#    """
#    google consent redirects to this route
#    this route redirects user to frontend
#    then frontend automatically makes google login
#    """
#
#    # TODO get access token from url
#
#    url_base = "http://localhost:3000/users/google_auth?"
#
#    url_params = {
#        "access_token": "qwqwq"
#    }
#
#    url_for_redirect = url_base + urllib.parse.urlencode(url_params)
#
#
#    return {
#        "test":"hello"
#    }



@auth_router.get("/google_auth_page")
def google_auth_test_page():
    """
    google consent screen redirects to this route
    this route page js redirects to frontend with token query parameter
    then that frontend makes request to "/google_login"
    """

    environment = Environment(loader=FileSystemLoader("apps/auth/templates/"))
    template = environment.get_template("google_auth.html")

    return HTMLResponse(
        template.render({
            "frontend_url_base" : "http://localhost:3000"
        })
    )




@auth_router.post("/google_login")
def google_login(
    access_token: str = fastapi.Body(embed=True),
    db: Session = Depends(get_db)
):
    
    """


    token info data example:
    {
        "issued_to": "12345.apps.googleusercontent.com",
        "audience": "12345.apps.googleusercontent.com",
        "user_id": "32321232",
        "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
        "expires_in": 3532,
        "email": "hello@gmail.com",
        "verified_email": true,
        "access_type": "online"
    }


    user data info example:
    {
        "id": "101990740313091496",
        "email": "hello@gmail.com",
        "verified_email": true,
        "name": "Alanominator kiborg",
        "given_name": "Alanominator",
        "family_name": "kiborg",
        "picture": "https://lh3.googleusercontent.com/a/ALm5wu0Id2J1nZHzDE2fZfAt1A2KiS-D5i85RcYNdTdk=s96-c",
        "locale": "en"
    }
    
    """



    url_google_tokeninfo = "https://www.googleapis.com/oauth2/v1/tokeninfo?"
    url_google_userinfo = "https://www.googleapis.com/oauth2/v1/userinfo?"

    REQUEST_RETRY_TRIES = 3
    REQUEST_RETRY_DELAY = 2


    # request token info
    try:
        @retry(delay = REQUEST_RETRY_DELAY, tries = REQUEST_RETRY_TRIES)
        def request_token_info():
            return requests.get(url=url_google_tokeninfo, params = {
                "access_token": access_token
            })

        token_info_response = request_token_info()
    except: # TODO catch exactly ConnectionError
        raise exceptions.network_connection_error


    # if status code != 200, raise error
    if token_info_response.status_code != 200:
        raise exceptions.google_invalid_token
    # assert token_info_response.status_code == 200


    # check if token's app is our app
    token_info = token_info_response.json()
    if token_info['issued_to'] != settings.GOOGLE_CLIENT_ID:
        raise exceptions.google_invalid_token


    # request user info
    try:
        @retry(delay = REQUEST_RETRY_DELAY, tries = REQUEST_RETRY_TRIES)
        def request_user_info():
            return requests.get(url=url_google_userinfo, params = {
                    "access_token": access_token
                })

        user_info_response = request_user_info()
    except: # TODO catch exactly ConnectionError
        raise exceptions.network_connection_error


    # if status code != 200, raise errror
    if user_info_response.status_code != 200:
        raise exceptions.google_invalid_token
    # assert user_info_response.status_code == 200


    # ======
    # ========================
    # EVERYTHING IS OK, we can continue

    goolge_user_info = user_info_response.json()

    google_user_email = goolge_user_info["email"]


    # try to get user
    db_user = crud.get_user_by_email(db, google_user_email)

    # if user doesn't exist, create user
    if not db_user:
        db_user = crud.create_user(db,
            email = google_user_email,
            password = utils.gen_string(15), # no matter what's password we store now
            is_active = True
        )

    # create jwt tokens and return them
    user_id = db_user.id
    jwt_tokens = utils.create_auth_session_and_get_jwt_tokens(user_id)


    user = schemas.UserResponse.parse_obj(db_user.__dict__).dict()


    return {
        "user": user,
        "jwt_tokens": jwt_tokens
    }




# TODO reset password




@auth_router.get("/get_user")
async def get_user(
    current_user = Depends(get_current_user)
):
    u = schemas.UserResponse.parse_obj(current_user.__dict__).dict()

    return u



# TODO
@auth_router.post("/refresh_tokens")
async def refresh_tokens(
    current_user = Depends(get_current_user),
    refresh_token: str = fastapi.Body(embed=True)
):
    new_jwt_tokens = utils.refresh_jwt_tokens(refresh_token)

    return {
        "user": current_user,
        "jwt_tokens": new_jwt_tokens
    }


@auth_router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    print(access_token)

    decoded_payload = jwt.decode(
        token = access_token,
        key = settings.SECRET_KEY
    )

    current_session_id = decrypt_string(decoded_payload["session_id"])

    # todo optimize - we make two quieries to database
    current_session = db.query(models.AuthSession).where(
        models.AuthSession.id == current_session_id
    ).first()

    db.delete(current_session)
    db.commit()


    return {}


@auth_router.post("/logout_all")
async def logout_all(
    current_user = Depends(get_current_user),
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    db.query(models.AuthSession).filter(
        models.AuthSession.user_id == current_user.id
    ).delete()

    db.commit()

    return {}



