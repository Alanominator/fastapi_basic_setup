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


chat_router = fastapi.APIRouter(
    prefix="/chat"
)






class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.websockets_group_by_room = {}
        self.user_info_by_websocket = {}


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

        # open db session and add user to session
        db = SessionLocal()
        db.add(
            user
        )

        # "user rooms" and "user rooms links" variables
        user_rooms = user.rooms
        user_rooms_links = [room.link for room in user_rooms]

        # close db session here
        db.close()

        # add websocket to websockets_group_by_rooms
        for room_link in user_rooms_links:
            if not room_link in self.websockets_group_by_room:
                self.websockets_group_by_room[room_link] = []
            self.websockets_group_by_room[room_link].append(websocket)

        # add user info to "user_info_by_websocket"
        self.user_info_by_websocket[id(websocket)] = {
            "db_user": user,
            "access_token_iat": access_token_iat,
            "rooms_links": user_rooms_links
        }

        # send "user rooms list" to user
        # TODO optimize - too much quieres to database
        user_rooms_list = [schemas.RoomResponse.parse_obj(room.__dict__).dict() for room in user_rooms]

        await manager.send_personal_message(
            websocket,
            {
                "action": "update_rooms_list",
                "data": user_rooms_list
            }
        )


    def disconnect(self, websocket: WebSocket):

        try:
            user_rooms_links_list = self.user_info_by_websocket[id(websocket)]["rooms_links"]

            for room_link in user_rooms_links_list:
                self.websockets_group_by_room[room_link].remove(websocket)

            del self.user_info_by_websocket[id(websocket)]

            self.active_connections.remove(websocket)
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
    
    access_token = data["access_token"]

    print(access_token)



async def user_is_typing(websocket: WebSocket, data):

    room_link = data["room_link"]

    if websocket in manager.websockets_group_by_room[room_link]:

        username = manager.user_info_by_websocket[id(websocket)]["db_user"].email # todo username

        print(username + " is typing in ", data["room_link"])

        await manager.broadcast_list_of_ws(
            manager.websockets_group_by_room[room_link],
            {
                "action": "user_is_typing",
                "data": {
                    "room_link": room_link,
                    "username": username
                }
            }
        )




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
