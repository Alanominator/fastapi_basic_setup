##### Folder structure for fastapi project


.
# setup

## create virtual env
```
virtualenv me
```

## activate virtual env
```
. me/bin/activate
```

## install requirements
```
pip3 install -r requirements/base.txt
```


## create database
```
```

## create .env file with these variables
```
DATABASE_URL = postgresql://user:password@localhost:5432/database_name
```


.
.



# make migrations

## create migration file
```
alembic revision --autogenerate -m 'comment'
```
## execute last migration file (head)
```
alembic upgrade head
```


# to run server
```
cd _src

uvicorn main:app --reload
```

