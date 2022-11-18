from unittest.result import failfast
from fastapi import FastAPI
from apps.auth.routers import auth_router

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
    auth_router,
])





# app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.106", port=8000)


