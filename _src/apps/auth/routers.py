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



auth_router = fastapi.APIRouter(
    prefix="/users"
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")



# TODO
"""
change some response status codes

fix schemes
"""




# TODO
@auth_router.get('/captcha', summary='captcha', name='captcha')
def get_captcha():
    img, text = img_captcha()

    # send hash of encrypted text
    # it is not safe

    return StreamingResponse(content=img, media_type='image/jpeg')








@auth_router.post("/register")
async def register_user(*,
    user: schemas.UserCreate = fastapi.Body(),
    db: Session = Depends(get_db)
):
    # todo recaptcha

    # check if user with given email exists, if yes, raise 400
    if ( crud.get_user_by_email(db, email = user.email) ):
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "message": "User with this email already exists"
            }
        )


    # validate email
    if not utils.isEmailValid(user.email):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
            detail = {
                "message": "Email is not valid"
            }
        )

    # validate password
    if not utils.isPasswordValid(user.password):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
            detail = {
                "message": "Password is invalid"
            }
        )

    # if password_confirmation not equals to password, raise error
    if not user.password == user.password_confirmation:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
            detail = {
                "message": "Password confirmation is not equal to password"
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





# resend activation password
# todo check activation token time







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


    db_token.user.is_active = True
    db.delete(db_token)
    db.commit()


    return {
        "hello": f"Your account has been activated"
    }




@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    email = form_data.username
    password = form_data.password

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


    return jwt_tokens



async def get_current_user(token: str = Depends(oauth2_scheme)):

    user = utils.get_user_by_access_token(
        access_token = token
    )

    return user


# @auth_router.get("/some_private_route")
# async def some_private_path(
#     current_user = Depends(get_current_user)
# ):
#     return current_user




@auth_router.get("/google_auth_consent", response_class=RedirectResponse)
def google_auth_consent():

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





# @auth_router.get("/google_auth_page") # response_class=RedirectResponse
# def google_auth_page():
    # """
    # function redirects user to frontend then frontend automatically makes google login
    # """

#     url_base = "http://localhost:8000/users/tmp_google_auth?"

#     url_params = {
#         "access_token": "qwqwq"
#     }

#     url_for_redirect = url_base + urllib.parse.urlencode(url_params)


#     return RedirectResponse(url_for_redirect)



@auth_router.get("/google_auth_page")
def google_auth_test_page():
    """
    for testing. But we use react app
    """

    environment = Environment(loader=FileSystemLoader("apps/auth/templates/"))
    template = environment.get_template("google_auth.html")

    return HTMLResponse(
        template.render()
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


    # TODO return user info with jwt_tokens
    return jwt_tokens


