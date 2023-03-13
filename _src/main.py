from fastapi import FastAPI

from apps.auth.routers import auth_router
from apps.chat.routers import chat_router

from core.utils import include_routers
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="Title",
    description="Description",
    version="1.0.0"
    # todo DOCUMENTATION
)
# TODO cors policy

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


include_routers(application=app, routers_to_include=[
    # routers to include ->>>
    auth_router,
    chat_router,
])



@app.get("/")
def hello():
    return {
        "message": "hello world"
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.106", port=8000)


