from typing import Union
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    last_read_chat_history_id: Union[int, None] = None
