from asyncio import sleep
import json
import fastapi
from fastapi import Depends, Cookie, WebSocket, WebSocketDisconnect
from typing import List

# from itsdangerous import exc


from ..auth.utils import get_user_by_access_token, get_time_has_passed_by_epoch_in_min


from jose import jwt

from core.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM



chat_router = fastapi.APIRouter(
    prefix="/chat"
)


"""
# todo

accept connection if authenticated
    else - deny

mongodb

send data to rooms (broadcast to user of room that are online)

"""

# from ..auth.routers import get_current_user




class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []


    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    

    def disconnect(self, websocket: WebSocket):
        # TODO remove key from user_info_by_websocket
        self.active_connections.remove(websocket)
    

    async def send_personal_message(self, websocket: WebSocket, message: str):
        if is_token_time_expired(websocket):
            websocket.close()

        await websocket.send_text(message)
    

    async def broadcast(self, message: str):

        # todo broadcast to users of room
        for connection in self.active_connections:
            
            if is_token_time_expired(connection):
                connection.close()

            await connection.send_text(message)




manager = ConnectionManager()



user_info_by_websocket = {
    "id_of_websocket": {
        "user": {
            "username": "alan",
        },
        "access_token_iat": 1231132,
    }
}


def add_or_update_user_info(websocket_id, access_token):
    user = get_user_by_access_token(access_token)
        
    decoded_payload = jwt.decode(
        token = access_token,
        key = SECRET_KEY
    )
    access_token_iat = decoded_payload["iat"]

    user_info_by_websocket[websocket_id]["user"] = user # TODO only certain fields
    user_info_by_websocket[websocket_id]["access_token_iat"] = access_token_iat






def is_token_time_expired(websocket: WebSocket):
    """
    
    returns "True" if the token time is expired, else - False

    """

    try:
        return get_time_has_passed_by_epoch_in_min(
            user_info_by_websocket[id(websocket)]["access_token_iat"]
        ) > ACCESS_TOKEN_EXPIRE_MINUTES
    except:
        return False



# ACTIONS ->>
# ______________________________

async def user_is_typing(websocket: WebSocket, data):
    print("user is typing in ", data["room_link"])

    # todo check if user in the room
    # todo broadcast to users of the room "user is typing"

    # await manager.broadcast("user is typing")


async def update_access_token(websocket: WebSocket, data):
    
    access_token = data["access_token"]

    try:
        add_or_update_user_info(
            id(websocket),
            access_token
        )
    except:
        websocket.close()



actions = {
    "user_is_typing": user_is_typing,
    "update_access_token": update_access_token,
}




@chat_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    # todo
    access_token = 'todo'


    try:
        # 
        add_or_update_user_info(
            id(websocket),
            access_token
        )

        # 
        await manager.connect(websocket)
    except:
        await websocket.close()



    async def run_action(action, data):
        if action and data:
            try:
                await actions[action](websocket, data)
            except KeyError:
                print("Unknown action ", action)


    try:
        while True:
            data = await websocket.receive_json()

            if is_token_time_expired(websocket):
                manager.disconnect(websocket)

            await run_action(
                data["action"],
                data["data"]
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
