from pydantic import BaseModel, constr

class ChatCreate(BaseModel):
    user_id: int
    message: constr(min_length=1)  # Ensure message is not empty
