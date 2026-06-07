from pydantic import BaseModel

class UserMod(BaseModel):
    username: str
    password: str

