from fastapi import APIRouter
from models import User
from schemas import UserCreator, User



api = APIRouter(
    prefix="/users",
)


@api.post("/", response_model=User)
async def create_user(user: UserCreator):
    user = await User.create(**user.dict())
    return user

@api.get("/{id}", response_model=User)
async def get_user(id: str):
    user = await User.get(id)
    return user


@api.get("/", response_model=list[User])
async def get_all_users():
    users = await User.get_all()
    return users


@api.put("/{id}", response_model=User)
async def update(id: str, user: UserCreator):
    user = await User.update(id, **user.dict())
    return user


@api.delete("/{id}", response_model=bool)
async def delete_user(id: str):
    return await User.delete(id)