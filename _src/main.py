from fastapi import FastAPI

from apps.auth.routers import auth_router
from apps.chat.routers import chat_router

from core.utils import include_routers



app = FastAPI(
    title="Title",
    description="Description",
    version="1.0.0",
    # routers=routers,
    # middleware=middleware
    # todo DOCUMENTATION
)


include_routers(application=app, routers_to_include=[
    # routers to include ->>>
    auth_router,
    chat_router,
])



@app.get("/")
def hello():
    return {
        "message": "hello world",
        "docs": "docs is located at '/docs'"
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.106", port=8000)


