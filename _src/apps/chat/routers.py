from asyncio import sleep
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
        self.active_connections: List[WebSocket] = []
        self.websockets_group_by_room = {}
        self.user_info_by_websocket = {}
        self.opened_groups_by_id = {}


    async def connect(self, websocket: WebSocket, access_token):
        await websocket.accept()

        self.active_connections.append(websocket)

        # get user by access token
        user = get_user_by_access_token(access_token)

        # get access token issued at field
        access_token_iat = jwt.decode(
            token = access_token,
            key = SECRET_KEY
        )["iat"]


        db = SessionLocal()
        db.add(
            user
        )


        user_rooms_list = [
            schemas.RoomResponse.parse_obj(room.__dict__).dict() 
                for room in 
                    db.query(models.Room).join(models.RoomMembers).where(models.Room.id == models.RoomMembers.room_id).where(models.RoomMembers.user_id == user.id)
        ]

        user_rooms_ids = [room["id"] for room in user_rooms_list]

        # add websocket to websockets_group_by_rooms
        for room_id in user_rooms_ids:
            if not room_id in self.websockets_group_by_room:
                self.websockets_group_by_room[room_id] = []
            self.websockets_group_by_room[room_id].append(websocket)

        
        # 
        # self.opened_groups_by_id
        for r in user_rooms_list:
            if not r["id"] in self.opened_groups_by_id:
                self.opened_groups_by_id[r["id"]] = r

        print(self.opened_groups_by_id)


        # add user info to "user_info_by_websocket"
        self.user_info_by_websocket[id(websocket)] = {
            "db_user": user,
            "access_token": access_token,
            "access_token_iat": access_token_iat,
            # "rooms": user_rooms_list,
            "rooms_ids": user_rooms_ids
        }


        print(user_rooms_list)
        
        db.close()

        await manager.send_personal_message(
            websocket,
            {
                "action": "update_rooms_list",
                "data": user_rooms_list
            }
        )
        
        

    def disconnect(self, websocket: WebSocket):

        try:
            user_rooms_ids = self.user_info_by_websocket[id(websocket)]["rooms_ids"]

            for room_id in user_rooms_ids:
                # 
                self.websockets_group_by_room[room_id].remove(websocket)

                if not len(self.websockets_group_by_room[room_id]):
                    del self.websockets_group_by_room[room_id]
                
                    #
                    del self.opened_groups_by_id[room_id]



            del self.user_info_by_websocket[id(websocket)]

            self.active_connections.remove(websocket)

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

    new_access_token = data["new_access_token"]
    current_access_token = user_info["access_token"]

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



async def get_last_messages_by_room(websocket: WebSocket, data):
    room_id = data["room_id"]
    count = data["count"]

    # restriction
    if count > 30:
        count = 30

    if not (room_id in manager.user_info_by_websocket[id(websocket)]["rooms_ids"]):
        return

    db = SessionLocal()
    
    messages = [{**schemas.MessageResponse.parse_obj(msg.__dict__).dict()}
        for msg in
            db.query(models.Message).where(models.Message.room_id == room_id).order_by(models.Message.id.desc()).limit(count)
    ]



    """
    SELECT messages.*, rooms.link AS room_link 
    FROM messages 
    JOIN rooms ON messages.room_id = rooms.id
    WHERE messages.room_id = 197
    ORDER BY messages.id DESC 
    LIMIT 15;
    
    """



    await manager.send_personal_message(websocket,
        {
            "action": "add_messages_to_room",
            "data": {
                "room_link": manager.opened_groups_by_id[room_id]["link"],
                "messages": messages
            }
        }
    )



async def get_messages_by_room_with_offset(websocket: WebSocket, data):
    room_id = data["room_id"]
    offset_id = data["offset_id"]
    count = data["count"]

    print(offset_id)

    # restriction
    if count > 30:
        count = 30

    if not (room_id in manager.user_info_by_websocket[id(websocket)]["rooms_ids"]):
        return

    db = SessionLocal()
    
    messages = [{**schemas.MessageResponse.parse_obj(msg.__dict__).dict()}
        for msg in
            db.query(models.Message).where(models.Message.room_id == room_id).where(models.Message.id < offset_id).order_by(models.Message.id.desc()).limit(count)
    ]

    print("\n", messages)

    await manager.send_personal_message(websocket,
        {
            "action": "add_messages_to_room",
            "data": {
                "room_link": manager.opened_groups_by_id[room_id]["link"],
                "messages": messages
            }
        }
    )

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



async def connect_to_room(websocket: WebSocket, data):
    room_link = data["room_link"]



async def load_data(websocket: WebSocket, data):
    data = data

    print("\n\n")
    # print(data)

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



actions = {
    "user_is_typing": user_is_typing,
    "update_access_token": update_access_token,
    "get_last_messages_by_room": get_last_messages_by_room,
    "get_messages_by_room_with_offset": get_messages_by_room_with_offset,
    "connect_to_room": connect_to_room,
    "load_data": load_data
}




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

            action = data["action"]
            data = data["data"]

            if action and data:
                if action in actions:
                    try:
                        await actions[action](websocket, data)
                    except Exception as e:
                        print(e)
                else:
                    print("Unknown action ", action)


    except WebSocketDisconnect:
        print("disconnect")
        manager.disconnect(websocket)



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
            "room_data": {
                "id": 999,
                "link": r.link,
                "name": r.name
            }
        }
    )

    return JSONResponse(
        status_code = 404,
        content ={
            "error_message": "Room is not found"
        }
    )