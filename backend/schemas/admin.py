from pydantic import BaseModel


class AdminLogin(BaseModel):
    password: str


class AdminToken(BaseModel):
    token: str
    expires_at: str
