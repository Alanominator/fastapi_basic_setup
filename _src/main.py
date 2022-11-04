import os
import uvicorn
from fastapi import FastAPI


from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db

from models import Student as StudentModel
from schemas import Student as StudentSchema



SQLALCHEMY_DATABASE_URL = "postgresql://alan:fastapi@localhost:5432/fastapi"

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=SQLALCHEMY_DATABASE_URL)

@app.post("/student/", response_model=StudentSchema)
def students(student: StudentSchema):


   student_model = StudentModel(
       first_name=student.first_name,
       last_name=student.last_name,
       age=student.age
   )
   
   db.session.add(student_model)
   db.session.commit()

   return student_model


if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)