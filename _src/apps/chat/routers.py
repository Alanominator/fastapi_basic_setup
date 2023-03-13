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


"""
# todo

accept connection if authenticated
    else - deny

mongodb

send data to rooms (broadcast to user of room that are online)

"""

# from ..auth.routers import get_current_user






opened_rooms = {
    # "room_link": ["websocket1", "websocket2"]
}

# users_info_by_websocket_id
user_info_by_websocket = {
    # "id_of_websocket": {
    #     "user": "user object"
    #     "db_user": "from database"
    #     "access_token_iat": 1231132,
    #     "rooms_links": []
    # }
}




class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []


    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    

    def disconnect(self, websocket: WebSocket):
        # TODO remove key from user_info_by_websocket

        user_rooms_links_list = user_info_by_websocket[id(websocket)]["rooms_links"]

        for room_link in user_rooms_links_list:
            opened_rooms[room_link].remove(websocket)

        del user_info_by_websocket[id(websocket)]

        self.active_connections.remove(websocket)
    

    async def send_personal_message(self, websocket: WebSocket, message: str):
        if is_token_time_expired(websocket):
            websocket.close()

        await websocket.send_text(message)
    

    # async def broadcast(self, message: str):

    #     for connection in self.active_connections:
            
    #         if is_token_time_expired(connection):
    #             connection.close()

    #         await connection.send_text(message)


    async def broadcast_list_of_ws(self, list_of_websockets: List[WebSocket], message):
        print("\n\n\nlist_of_websockets - ", list_of_websockets)

        for ws in list_of_websockets:
            if is_token_time_expired(ws):
                print("\n\n\n closing connection")
                # await ws.close()
            else:
                await ws.send_json(message)



manager = ConnectionManager()




def add_or_update_user_info(websocket_id, access_token):

    user = get_user_by_access_token(access_token)

    decoded_payload = jwt.decode(
        token = access_token,
        key = SECRET_KEY
    )


    access_token_iat = decoded_payload["iat"]

    
    user_info_by_websocket[websocket_id] = {
        # "user": schemas.UserInfoByWS.parse_obj(user.__dict__).dict(),
        "db_user": user,
        "access_token_iat": access_token_iat
    }








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

    # todo check if user in the room
    # todo broadcast to users of the room "user is typing"

    room_link = data["room_link"]

    if websocket in opened_rooms[room_link]:
        print("user is typing in ", data["room_link"])

        username = user_info_by_websocket[id(websocket)]["db_user"].email

        await manager.broadcast_list_of_ws(
            opened_rooms[room_link],
            {
                "action": "user_is_typing",
                "data": {
                    "room_link": room_link,
                    "username": username
                }
            }
        )



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




@chat_router.websocket(f"/")
async def websocket_endpoint(websocket: WebSocket):

    access_token = websocket.cookies.get("access_token")

    print(websocket.cookies)

    if not access_token:
        await websocket.close()
        return


    try:
        # 
        add_or_update_user_info(
            id(websocket),
            access_token
        )
        

        db = SessionLocal()

        user = user_info_by_websocket[id(websocket)]["db_user"]

        db.add(
            user
        )

        user_rooms = user.rooms

        for room_link in [r.link for r in user_rooms]:
            if not room_link in opened_rooms:
                opened_rooms[room_link] = []
            opened_rooms[room_link].append(websocket)

        rooms_list = [schemas.RoomResponse.parse_obj(room.__dict__).dict() for room in user_rooms]

        user_info_by_websocket[id(websocket)]["rooms_links"] = [room.link for room in user_rooms]

        await manager.connect(websocket)
        
        await websocket.send_json({
            "action": "update_rooms_list",
            "data": rooms_list
        })

        print([schemas.RoomResponse.parse_obj(room.__dict__).dict() for room in user_rooms])

    except Exception as e:
        print(e)
        return
    


    try:
        while True:
            data = await websocket.receive_json()

            if is_token_time_expired(websocket):
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
