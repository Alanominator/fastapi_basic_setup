from asyncio import sleep
import json
import fastapi
from fastapi import Depends, Cookie, WebSocket, WebSocketDisconnect
from typing import List

from core.config.database.database import SessionLocal

# from itsdangerous import exc


from ..auth.utils import get_user_by_access_token, get_time_has_passed_by_epoch_in_min


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
                    db.query(models.Room).join(models.RoomMembers).where(models.Room.id == models.RoomMembers.room_id).where(models.RoomMembers.user_id == 10)
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

        await websocket.send_json(message)


    async def broadcast_list_of_ws(self, list_of_websockets: List[WebSocket], message):

        for ws in list_of_websockets:
            if self.is_token_time_expired_by_websocket(ws):
                print("\n\n\n closing connection")
                await ws.close()
            else:
                await ws.send_json(message)


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
            manager.websockets_group_by_room[room_id],
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

    # select * from messages where room_id = 3  order by id desc  limit 15;



async def get_messages_by_room_with_offset(websocket: WebSocket, data):
    room_id = data["room_id"]
    id_offset = data["id_offset"]

    # select * from messages where messages.room_id = 3 and messages.id < 15143 order by id desc limit 15;





actions = {
    "user_is_typing": user_is_typing,
    "update_access_token": update_access_token,
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
