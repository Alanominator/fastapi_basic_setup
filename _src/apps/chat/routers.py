from asyncio import sleep
from decimal import DivisionByZero
import json
import fastapi
from fastapi import Depends, Cookie, WebSocket, WebSocketDisconnect
from typing import List

from core.config.database.database import SessionLocal
from ..auth.routers import get_current_user

from sqlalchemy.orm import Session

from core.config.database.utils import get_db

# from itsdangerous import exc


from ..auth.utils import get_user_by_access_token, get_time_has_passed_by_epoch_in_min


from fastapi.responses import JSONResponse, RedirectResponse

from fastapi import Depends, HTTPException, status
from jose import jwt

from core.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from . import schemas
from . import models
from .. import auth




chat_router = fastapi.APIRouter(
    prefix="/chat"
)



"""
#TODO

room_link -> room_id

left join

"""




class ConnectionManager:
    def __init__(self):
        """
        
        {'1': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '2': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '4': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '5': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '6': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '7': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '9': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '10': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '12': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '13': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '18': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '19': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '21': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '25': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>], '26': [<starlette.websockets.WebSocket object at 0x7f5d6430dfa0>]}
        
        {140039089610656: {'db_user': <apps.auth.models.User object at 0x7f5d6432c130>, 'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJzZXNzaW9uX2lkIjoiZ0FBQUFBQmtHWXFoSlo4ZW9LbXVIUUVvOERpVUlCT1NybC16WkdRMXA0ZkROUnZfNTVkOHhMc1IybzhiVERQTGlZTWthOUdrY2Rpc1FZTXNyNEQzRzZwekhWWkhYUjYtdUE9PSIsImlhdCI6MTY3OTM5NTQ4OSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.cX4yBiAxTBg7p5kAGmrGxZmHfQV4AZOa_D04Pjz8m1I', 'access_token_iat': 1679395489, 'rooms_ids': ['1', '2', '4', '5', '6', '7', '9', '10', '12', '13', '18', '19', '21', '25', '26']}}
        
        {'1': {'id': '1', 'name': 'autem ', 'link': 'kyejfdabbfbxa', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '2': {'id': '2', 'name': 'persp ', 'link': 'tfssufznfqyj', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '4': {'id': '4', 'name': 'volup optio ', 'link': 'upderdxp', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '5': {'id': '5', 'name': 'Saepe ', 'link': 'yyxvdtgw', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '6': {'id': '6', 'name': 'maior accus ', 'link': 'ejwiplagdjux', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '7': {'id': '7', 'name': 'error ', 'link': 'zcwikinxndp', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '9': {'id': '9', 'name': 'dolor ', 'link': 'wotufbn', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '10': {'id': '10', 'name': 'rem ', 'link': 'mbodbirwql', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 34, 51, 338597)}, '12': {'id': '12', 'name': 'exerc ', 'link': 'yerkvqninp', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 35, 20, 519312)}, '13': {'id': '13', 'name': 'saepe at ', 'link': 'rkbfnex', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 35, 20, 519312)}, '18': {'id': '18', 'name': 'magni venia ', 'link': 'scvtevyginhen', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 35, 20, 519312)}, '19': {'id': '19', 'name': 'Molli ', 'link': 'nmkeiarflf', 'description': None, 'created_at': datetime.datetime(2023, 3, 20, 13, 35, 20, 519312)}, '21': {'id': '21', 'name': 'provi ', 'link': 'rvstzgrfjo', 'description': None, 'created_at': datetime.datetime(2023, 3, 21, 10, 24, 18, 633202)}, '25': {'id': '25', 'name': 'enim, ', 'link': 'cgavyul', 'description': None, 'created_at': datetime.datetime(2023, 3, 21, 10, 24, 18, 633202)}, '26': {'id': '26', 'name': 'iusto ', 'link': 'uizzlhdlxml', 'description': None, 'created_at': datetime.datetime(2023, 3, 21, 10, 24, 18, 633202)}}


        
        """

        self.websockets_group_by_room = {}
        self.user_info_by_websocket = {}
        self.opened_groups_by_id = {}


    async def connect(self, websocket: WebSocket, access_token):
        await websocket.accept()

        # get user by access token
        user = get_user_by_access_token(access_token)

        # # get access token issued at field
        access_token_iat = jwt.decode(
            token = access_token,
            key = SECRET_KEY
        )["iat"]

        self.user_info_by_websocket[id(websocket)] = {
            "db_user": user,
            "access_token": access_token,
            "access_token_iat": access_token_iat,
            "rooms_ids": []
        }


        await update_rooms_list(websocket, {})
        

    def disconnect(self, websocket: WebSocket):

        try:
            user_rooms_ids = self.user_info_by_websocket[id(websocket)]["rooms_ids"]

            for room_id in user_rooms_ids:
                # 
                self.websockets_group_by_room[room_id].remove(websocket)

                if not len(self.websockets_group_by_room[room_id]):
                    del self.websockets_group_by_room[room_id]
                    del self.opened_groups_by_id[room_id]


            del self.user_info_by_websocket[id(websocket)]

            # self.active_connections.remove(websocket)

            print(self.opened_groups_by_id)
        except Exception as e:
            print(e)

        


    async def send_personal_message(self, websocket: WebSocket, message: str):
        if self.is_token_time_expired_by_websocket(websocket):
            websocket.close()

        await websocket.send_text(json.dumps(message, default=str))


    async def broadcast_list_of_ws(self, list_of_websockets: List[WebSocket], message):

        for ws in list_of_websockets:
            if self.is_token_time_expired_by_websocket(ws):
                print("\n\n\n closing connection")
                await ws.close()
            else:
                await ws.send_text(json.dumps(message, default=str))


    def is_token_time_expired_by_websocket(self, websocket: WebSocket) -> bool:
        """
        
        returns "True" if the token time is expired, else - False

        """

        try:
            return get_time_has_passed_by_epoch_in_min(
                self.user_info_by_websocket[id(websocket)]["access_token_iat"]
            ) > ACCESS_TOKEN_EXPIRE_MINUTES
        except:
            return False





manager = ConnectionManager()



# ACTIONS ->>
# ______________________________

async def update_access_token(websocket: WebSocket, data):

    user_info = manager.user_info_by_websocket[id(websocket)]

    current_access_token = user_info["access_token"]
    new_access_token = data["new_access_token"]

    if new_access_token != current_access_token:
        
        # try to get user by access token
        get_user_by_access_token(new_access_token)

        # get access token issued at field
        new_access_token_iat = jwt.decode(
            token = new_access_token,
            key = SECRET_KEY
        )["iat"]

        # update access token info
        user_info["access_token"] = new_access_token
        user_info["access_token_iat"] = new_access_token_iat

        print("--- OK, token updated")



async def update_rooms_list(websocket: WebSocket, data):
    print("\n\n\n\n\tUPDATE ROOMS LIST\n\n\n")

    db = SessionLocal()

    user = manager.user_info_by_websocket[id(websocket)]["db_user"]

    user_rooms_list = [
        schemas.RoomResponse.parse_obj(room.__dict__).dict() 
            for room in 
                db.query(models.Room).join(models.RoomMembers).where(models.Room.id == models.RoomMembers.room_id).where(models.RoomMembers.user_id == user.id)
    ]

    db.close()

    user_rooms_ids = [room["id"] for room in user_rooms_list]

    # add websocket to websockets_group_by_rooms
    for room_id in user_rooms_ids:
        if not room_id in manager.websockets_group_by_room:
            manager.websockets_group_by_room[room_id] = []
        manager.websockets_group_by_room[room_id].append(websocket)


    # self.opened_groups_by_id
    for r in user_rooms_list:
        if not r["id"] in manager.opened_groups_by_id:
            manager.opened_groups_by_id[r["id"]] = r


    # add user info to "user_info_by_websocket"
    manager.user_info_by_websocket[id(websocket)]["rooms_ids"] = user_rooms_ids


    await manager.send_personal_message(
        websocket,
        {
            "action": "update_rooms_list",
            "data": user_rooms_list
        }
    )



async def user_is_typing(websocket: WebSocket, data):

    room_id = data["room_id"]

    room_link = manager.opened_groups_by_id[room_id]["link"]

    if websocket in manager.websockets_group_by_room[room_id]:

        username = manager.user_info_by_websocket[id(websocket)]["db_user"].email # todo username

        print(username + " is typing in ", data["room_id"])

        await manager.broadcast_list_of_ws(
            [ws for ws in manager.websockets_group_by_room[room_id] if ws != websocket],
            {
                "action": "user_is_typing",
                "data": {
                    "room_link": room_link,
                    "username": username
                }
            }
        )



async def load_data(websocket: WebSocket, data):
    data = data

    db = SessionLocal()
    for room_id in data.keys():
        d = data[room_id]


        # if is user is not in this group, ignore
        if not websocket in manager.websockets_group_by_room[room_id]:
            continue


        if "messages_to_create" in d:
            messages = []

            for x in d['messages_to_create']:
                m = models.Message(
                    user_id = manager.user_info_by_websocket[id(websocket)]["db_user"].id,
                    room_id = room_id,
                    message_data = {
                        "message_type": x["message_type"],
                        "text": x["text"]
                    }
                )
                # ! 
                # TODO OPTIMIZE
                db.add(m)
                db.commit()
                db.refresh(m)
                
                messages.append(
                    schemas.MessageResponse.parse_obj(m.__dict__).dict()
                )


            await manager.broadcast_list_of_ws(manager.websockets_group_by_room[room_id],
                {
                "action": "add_messages_to_room",
                    "data": {
                        "room_link": manager.opened_groups_by_id[room_id]["link"],
                        "messages": messages
                    }
                }
            )
        # _______

        # for x in d['messages_ids_to_delete']:
        #     pass
        #     # print(m)
        
        # for x in d['messages_to_edit']:
        #     pass
        #     # print(m)
    

    db.close()



# ___________________
actions = {
    "user_is_typing": user_is_typing,
    "update_access_token": update_access_token,
    "update_rooms_list": update_rooms_list,
    # "get_last_messages_by_room": get_last_messages_by_room,
    # "get_messages_by_room_with_offset": get_messages_by_room_with_offset,
    "load_data": load_data
}
# _______________________________



@chat_router.websocket(f"/")
async def websocket_endpoint(websocket: WebSocket):

    access_token = websocket.cookies.get("access_token")

    if not access_token:
        await websocket.close()
        return


    try:
        await manager.connect(websocket, access_token)
    except Exception as e:
        print(e)
        manager.disconnect(websocket)
        return


    try:
        while True:
            data = await websocket.receive_json()

            if manager.is_token_time_expired_by_websocket(websocket):
                manager.disconnect(websocket)


            if "action" in data and "data" in data:
                if data["action"] in actions:
                    try:
                        await actions[
                            data["action"]
                        ](websocket, data["data"])
                    except DivisionByZero as e:
                        print(e)
                else:
                    print("Unknown action ", data["action"])


    except WebSocketDisconnect:
        print("disconnect")
        manager.disconnect(websocket)



# HTTP routes ____________________________

@chat_router.get("/get_room_data/")
async def get_room_data(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    room_link: str
):
    if not room_link:
        return JSONResponse(
            status_code = 404,
            content ={
                "error_message": "Room is not found"
            }
        )

    r = db.query(models.Room).\
        filter(models.Room.link == room_link).\
            first()


    if r:
        return JSONResponse(
        status_code = 200,
        content = {
            "room_data": json.dumps(
                    schemas.RoomResponse.parse_obj(r.__dict__).dict(),
                    default=str
                )
        }
    )

    return JSONResponse(
        status_code = 404,
        content ={
            "error_message": "Room is not found"
        }
    )




@chat_router.get("/join_room/")
async def join_room(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    room_link: str
):
    if not room_link:
        return JSONResponse(
            status_code = 404,
            content ={
                "error_message": "Room is not found"
            }
        )

    r = db.query(models.Room).\
        filter(models.Room.link == room_link).\
            first()


    if r:
        exists = db.query(models.RoomMembers).\
        filter(models.RoomMembers.room_id == r.id).\
            filter(models.RoomMembers.user_id == current_user.id).\
            first()

        if not exists:
            new_room_members_relation = models.RoomMembers(
                user_id = current_user.id,
                room_id = r.id
            )
            db.add(new_room_members_relation)
            db.commit()

        return JSONResponse(
        status_code = 200,

        # TODO
        content = {
            "message": "success"
        }
    )

    return JSONResponse(
        status_code = 404,
        content ={
            "error_message": "Room is not found"
        }
    )




@chat_router.get("/chat_with_me/")
async def chat_with_me(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    # ! Vulnerability
    room_link = "chat_with_me_" + str(current_user.id)

    r = db.query(models.Room).\
        filter(models.Room.link == room_link).\
            first()

    if not r:
        r = models.Room(
            name = "Chat with me",
            link = room_link,
        )
        db.add(r)
        db.commit()
        db.refresh(r)


    user_in_room = db.query(models.RoomMembers).\
        filter(models.RoomMembers.room_id == r.id).\
            filter(models.RoomMembers.user_id == current_user.id).\
            first()

    if not user_in_room:
        # add user to room
        new_room_members_relation = models.RoomMembers(
            user_id = current_user.id,
            room_id = r.id
        )
        db.add(new_room_members_relation)
        db.commit()

    
    # TODO add admins to room
    admins = db.query(auth.models.User).filter(
        auth.models.User.is_admin == True
    )

    # TODO when some admin logins, add him to chats with link "chat_with_me"
    # TODO deny getting and creating rooms with link "chat_with_me"

    
    return JSONResponse(
        status_code = 200,

        # TODO
        content = {
            "room_link": room_link
        }
    )




@chat_router.get("/get_last_messages/")
async def get_last_messages(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    room_id:int,
    count:int=30
):
    # room_id = str(data["room_id"])
    # count = data["count"]

    # restriction
    if count > 30:
        count = 30

    # TODO check if group exists
    # TODO if user in this group

    
    messages = [{**schemas.MessageResponse.parse_obj(msg.__dict__).dict()}
        for msg in
            db.query(models.Message)\
                .where(models.Message.room_id == room_id)\
                    .order_by(models.Message.id.desc())\
                        .limit(count)
    ]


    """
    SELECT messages.*, rooms.link AS room_link 
    FROM messages 
    JOIN rooms ON messages.room_id = rooms.id
    WHERE messages.room_id = 197
    ORDER BY messages.id DESC 
    LIMIT 15;
    
    """



    return JSONResponse(
        status_code=200,
        content={
            "messages": json.dumps(messages, default=str)
        }
    )



@chat_router.get("/get_messages_with_offset/")
async def get_messages_with_offset(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    room_id:int,
    offset_message_id: int,
    count:int=30
):

    # restriction
    if count > 30:
        count = 30


    # TODO check if group exists
    # TODO if user in this group

    
    messages = [{**schemas.MessageResponse.parse_obj(msg.__dict__).dict()}
        for msg in
            db.query(models.Message)\
                .where(models.Message.room_id == room_id)\
                    .where(models.Message.id < offset_message_id)\
                        .order_by(models.Message.id.desc())\
                            .limit(count)
    ]

    """
    SELECT messages.*, rooms.link AS room_link 
    FROM messages 
    JOIN rooms ON messages.room_id = rooms.id
    WHERE messages.room_id = 197 AND messages.id < 1514323232
    ORDER BY messages.id DESC 
    LIMIT 15;
    
    """
    # select messages.*, rooms.link as room_link from messages join rooms on messages.room_id = rooms.id;
    # select * from messages where messages.room_id = 3 and messages.id < 15143 order by id desc limit 15;

    return JSONResponse(
        status_code=200,
        content={
            "offset_message_id": offset_message_id,
            "count": count,
            "messages": json.dumps(messages, default=str)
        }
    )




@chat_router.get("/get_messages_from_offset/")
async def get_messages_from_offset(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    room_id:int,
    offset_message_id: int,
    count:int=30
):

    # restriction
    if count > 30:
        count = 30


    # TODO check if group exists
    # TODO if user in this group

    
    messages = [{**schemas.MessageResponse.parse_obj(msg.__dict__).dict()}
        for msg in
            db.query(models.Message)\
                .where(models.Message.room_id == room_id)\
                    .where(models.Message.id > offset_message_id)\
                        # .order_by(models.Message.id.desc())\
                            .limit(count)
    ]

    """
    SELECT messages.*, rooms.link AS room_link 
    FROM messages 
    JOIN rooms ON messages.room_id = rooms.id
    WHERE messages.room_id = 197 AND messages.id > 6173
    ORDER BY messages.id DESC 
    LIMIT 15;
    
    """
    # select messages.*, rooms.link as room_link from messages join rooms on messages.room_id = rooms.id;
    # select * from messages where messages.room_id = 3 and messages.id < 15143 order by id desc limit 15;

    return JSONResponse(
        status_code=200,
        content={
            "room_id": room_id,
            "offset_message_id": offset_message_id,
            "count": count,
            "messages": json.dumps(messages, default=str)
        }
    )
