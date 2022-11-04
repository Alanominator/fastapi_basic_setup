https://github.com/zhanymkanov/fastapi-best-practices#1-project-structure-consistent--predictable



# create virtual env
virtualenv me

# activate virtual env
. me/bin/activate

# install requirements
pip3 install -r requirements/base.txt



# create database


```
DATABASE_URL = postgresql://alan:fastapi@localhost:5432/fastapi
```






# make migrations

## create migration file
alembic revision --autogenerate -m 'comment'

## execute last migration file (head)
alembic upgrade head


