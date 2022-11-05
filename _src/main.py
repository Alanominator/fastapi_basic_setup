import uvicorn
from fastapi import FastAPI
from core.database import *


app = FastAPI()


@app.get("/")
async def main():
   return {
      "hello":"world"
   }

if __name__ == "__main__":
   uvicorn.run(app, host="192.168.0.106", port=8000)