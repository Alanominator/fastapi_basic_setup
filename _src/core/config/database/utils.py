from .database import SessionLocal, AsyncSessionLocal


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


async def async_get_db():
    async with AsyncSessionLocal() as db:
        yield db
        await db.commit()