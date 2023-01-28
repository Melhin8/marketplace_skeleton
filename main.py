from database import db
from fastapi import FastAPI


def init_app():
    db.init()

    app = FastAPI(
        title="Melhin8 App",
        description="CRUD skelet of marketplace",
        version="1",
    )

    @app.on_event("startup")
    async def startup():
        await db.create_all()

    @app.on_event("shutdown")
    async def shutdown():
        await db.close()

    return app


app = init_app()