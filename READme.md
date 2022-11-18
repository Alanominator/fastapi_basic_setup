##### Folder structure for fastapi project, integrated with postgres, rabbimq

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


## create postgres database
```
```

## create rabbitmq virtual host
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


# run server
```
cd _src

uvicorn main:app --host=192.168.0.106 --port=8000 --reload
```

# run celery
celery -A celery_app  worker -l INFO